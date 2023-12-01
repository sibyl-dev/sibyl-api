import os
import pickle
import sys
from tqdm import tqdm

import numpy as np
import pandas as pd
import yaml
from mongoengine import connect
from pymongo import MongoClient
from pyreal import RealApp
from pyreal.transformers import (
    Mappings,
    MappingsOneHotDecoder,
    MappingsOneHotEncoder,
    MultiTypeImputer,
    run_transformers,
)
from sklearn.linear_model import LinearRegression

from sibyl.db import schema
from sibyl.db.utils import ModelWrapperThresholds
from sibyl.utils import get_project_root


def _load_data(features, dataset_filepath, target):
    data = pd.read_csv(dataset_filepath)

    y = data[target]
    X = data[features]

    return X, y


def _load_model_from_weights_sklearn(weights_filepath, model_base):
    """
    Load the model
    :return: (model, model features)
    """
    model_weights = pd.read_csv(weights_filepath)

    model = model_base
    dummy_X = pd.DataFrame(
        np.zeros((1, model_weights.shape[0] - 1)), columns=model_weights["weight"][1:]
    )
    dummy_y = np.zeros(1)
    model.fit(dummy_X, dummy_y)

    model.coef_ = np.array(model_weights["weight"][1:])
    model.intercept_ = model_weights["weight"][0]
    return model, model_weights["name"][1:]


def _validate_model_and_explainer(explainer, train_dataset):
    """
    Run predict and explain processes to make sure everything is working correctly
    """
    explainer.predict(train_dataset.iloc[0:2])
    explainer.produce_feature_contributions(train_dataset.iloc[0:2])
    print("Model predict and produce validated")


def insert_features(filepath):
    try:
        features_df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Features file {filepath} not found. Must provide valid features file"
        )
    items = features_df.to_dict(orient="records")
    schema.Feature.insert_many(items)
    return features_df["name"].tolist()


def insert_categories(filepath):
    if filepath is None:
        return
    try:
        cat_df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"Categories file {filepath} not found. ")
    items = cat_df.to_dict(orient="records")
    schema.Category.insert_many(items)


def insert_context(context_config_fp):
    if context_config_fp is None:
        return
    try:
        context_config = yaml.safe_load(open(context_config_fp, "r"))
    except FileNotFoundError:
        raise FileNotFoundError(f"Context config file {context_config_fp} not found. ")

    schema.Context.insert(configs=context_config)


def insert_entities(entity_fp, target=None, num=None, pbar=None, total_time=30):
    try:
        entity_df = pd.read_csv(entity_fp)
    except FileNotFoundError:
        raise FileNotFoundError(f"Entities file {entity_fp} not found. Must provide valid file.")

    if num is not None:
        entity_df = entity_df.sample(num)
    eids = entity_df["eid"]

    if "row_id" not in entity_df:
        entity_df["row_id"] = pd.Series(np.arange(0, entity_df.shape[0])).astype(str)
        use_rows = False
    else:
        entity_df["row_id"] = entity_df["row_id"].astype(str)
        use_rows = True

    entity_df = entity_df.set_index(["eid", "row_id"])
    raw_entities = {
        level: entity_df.xs(level).to_dict("index") for level in entity_df.index.levels[0]
    }

    entities = []
    for i, eid in enumerate(raw_entities):
        entity = {"eid": str(eid), "row_ids": list(raw_entities[eid].keys())}
        targets = {}
        for row_id in raw_entities[eid]:
            if target in raw_entities[eid][row_id]:
                targets[row_id] = raw_entities[eid][row_id].pop(target)
        entity["features"] = raw_entities[eid]
        entity["labels"] = targets
        entities.append(entity)
        if pbar:
            pbar.update(total_time / len(raw_entities))
    schema.Entity.insert_many(entities)
    return eids, use_rows


def insert_training_set(eids, target):
    references = [schema.Entity.find_one(eid=str(eid)) for eid in eids]
    training_set = {"entities": references, "target": target}

    set_doc = schema.TrainingSet.insert(**training_set)
    return set_doc


def insert_model(
    features,
    dataset_fp,
    target,
    set_doc,
    model_id=None,
    pickle_model_fp=None,
    weights_fp=None,
    threshold_fp=None,
    one_hot_encode_fp=None,
    model_transformers_fp=None,
    importance_fp=None,
    explainer_fp=None,
    shap_type=None,
    training_size=None,
    impute=None,
    prefit_se=True,
):
    model_features = features
    model = None

    # Base model options
    if pickle_model_fp is not None:
        # Load from pickle file
        print("Loading model from pickle file.")
        model = pickle.load(open(pickle_model_fp, "rb"))
    elif weights_fp is not None:
        # Load from list of weights
        print("Loading model from weights")
        model, model_features = _load_model_from_weights_sklearn(weights_fp, LinearRegression())

    # Model wrapping options
    if threshold_fp is not None and model is not None:
        # Bin output based on thresholds
        threshold_df = pd.read_csv(threshold_fp)
        thresholds = threshold_df["thresholds"].tolist()
        model = ModelWrapperThresholds(model, thresholds, features=model_features)

    train_dataset, targets = _load_data(features, dataset_fp, target)
    transformers = []

    if impute:
        imputer = MultiTypeImputer()
        imputer = imputer.fit(train_dataset)
        transformers.append(imputer)

    if one_hot_encode_fp is not None:
        mappings = pd.read_csv(one_hot_encode_fp)
        if "include" in mappings:
            mappings = mappings[mappings["include"]]
        transformer = MappingsOneHotEncoder(Mappings.generate_mappings(dataframe=mappings))
        transformers.append(transformer)

    if model_transformers_fp is not None:
        transformers = pickle.load(open(model_transformers_fp, "rb"))

    model_serial = None
    if model is not None:
        model_serial = pickle.dumps(model)

    texts = {
        "description": "placeholder",
        "performance": "placeholder",
    }
    description = texts["description"]
    performance = texts["performance"]
    if model_id is None:
        model_id = "model"

    if explainer_fp is not None:
        print("Loading explainer from file")
        with open(explainer_fp, "rb") as f:
            explainer_serial = f.read()
            explainer = pickle.loads(explainer_serial)
            explainer.id_column = "eid"
    else:
        # TODO: add additional explainers/allow for multiple algorithms
        explainer = RealApp(model, transformers=transformers, id_column="eid")
        explainer.prepare_feature_contributions(
            model_id=0,
            shap_type=shap_type,
            x_train_orig=train_dataset,
            y_train=targets,
            training_size=training_size,
        )
        explainer.prepare_feature_importance(
            model_id=0,
            shap_type=shap_type,
            x_train_orig=train_dataset,
            y_train=targets,
            training_size=training_size,
        )
        if prefit_se:
            explainer.prepare_similar_examples(
                model_id=0,
                x_train_orig=train_dataset,
                y_train=targets,
                training_size=training_size,
                standardize=True,
            )
        explainer_serial = pickle.dumps(explainer)

    # Check that everything is working correctly
    _validate_model_and_explainer(explainer, train_dataset)

    if importance_fp is not None:
        importance_df = pd.read_csv(importance_fp)
        importance_df = importance_df.set_index("name")
    else:
        importance_dict = explainer.produce_feature_importance()
        importance_df = pd.DataFrame.from_dict(importance_dict)
        importance_df = importance_df.rename(
            columns={"Feature Name": "name", "Importance": "importance"}
        )
        importance_df.set_index("name")

    importances = importance_df.to_dict(orient="dict")["importance"]

    items = {
        "model": model_serial,
        "model_id": model_id,
        "importances": importances,
        "description": description,
        "performance": performance,
        "explainer": explainer_serial,
        "training_set": set_doc,
    }
    schema.Model.insert(**items)
    return explainer


def prepare_database(config_file, directory=None):
    def _process_fp(fn):
        if fn is not None:
            return os.path.join(directory, fn)
        return None

    times = {
        "Categories": 2,
        "Features": 3,
        "Context": 2,
        "Entities": 20,
        "Training Set": 20,
    }
    pbar = tqdm(total=sum(times.values()))

    with open(config_file, "r") as f:
        cfg = yaml.safe_load(f)

    # Begin database loading ---------------------------
    database_name = cfg["database_name"]
    if directory is None:
        if cfg.get("directory") is None:
            directory = os.path.join(get_project_root(), "dbdata", database_name)
        else:
            directory = os.path.join(get_project_root(), "dbdata", cfg["directory"])

    if cfg.get("DROP_OLD", False):
        client = MongoClient("localhost", 27017)
        client.drop_database(database_name)
    connect(database_name, host="localhost", port=27017)

    # INSERT CATEGORIES, IF PROVIDED
    pbar.set_description("Inserting categories...")
    insert_categories(_process_fp(cfg.get("categories_fn")))
    pbar.update(times["Categories"])

    # INSERT FEATURES
    pbar.set_description("Inserting features...")
    insert_features(_process_fp(cfg.get("features_fn", "features.csv")))
    pbar.update(times["Features"])

    # INSERT CONTEXT
    pbar.set_description("Inserting context...")
    insert_context(_process_fp(cfg.get("context_config_fn")))
    pbar.update(times["Context"])

    # INSERT ENTITIES
    pbar.set_description("Inserting entities...")
    eids, use_rows = insert_entities(
        _process_fp(cfg.get("entity_fn", "entities.csv")),
        target=cfg.get("target", "target"),
        pbar=pbar,
        total_time=times["Entities"],
    )

    # INSERT FULL DATASET
    pbar.set_description("Inserting training set...")
    if cfg.get("include_database", False) and cfg.get("training_entities_fn"):
        eids = insert_entities(
            _process_fp(cfg.get("training_entities_fn")),
            target=cfg.get("target", "target"),
            pbar=pbar,
            total_time=times["Training Set"],
        )
    else:
        pbar.update(times["Training Set"])

    set_doc = insert_training_set(eids, cfg.get("target"))


"""

    # INSERT MODEL
    if cfg.get("explainer_directory_name") is not None:
        explainer_directory = _process_fp(cfg.get("explainer_directory_name"))
        for explainer_file in os.listdir(explainer_directory):
            if explainer_file.endswith(".pkl"):
                insert_model(
                    feature_names,
                    dataset_fp,
                    target,
                    set_doc,
                    model_id=explainer_file[:-4],  # remove .pkl
                    importance_fp=_process_fp(cfg.get("importance_fn")),
                    explainer_fp=os.path.join(explainer_directory, explainer_file),
                    one_hot_encode_fp=_process_fp(cfg.get("one_hot_encode_fn")),
                    shap_type=cfg.get("shap_type"),
                    training_size=cfg.get("training_size"),
                    impute=cfg.get("impute", False),
                    prefit_se=cfg.get("prefit_se", True),
                )
    elif cfg.get("model_directory_name") is not None:
        model_directory = _process_fp(cfg.get("model_directory_name"))
        for model_file in os.listdir(model_directory):
            if model_file.endswith(".pkl"):
                insert_model(
                    feature_names,
                    dataset_fp,
                    target,
                    set_doc,
                    model_id=model_file[:-4],  # remove .pkl
                    pickle_model_fp=os.path.join(model_directory, model_file),
                    importance_fp=_process_fp(cfg.get("importance_fn")),
                    explainer_fp=_process_fp(cfg.get("explainer_fn")),
                    one_hot_encode_fp=_process_fp(cfg.get("one_hot_encode_fn")),
                    shap_type=cfg.get("shap_type"),
                    training_size=cfg.get("training_size"),
                    impute=cfg.get("impute", False),
                    prefit_se=cfg.get("prefit_se", True),
                )
    else:
        insert_model(
            feature_names,
            dataset_fp,
            target,
            set_doc,
            model_id=cfg.get("model_name"),
            pickle_model_fp=_process_fp(cfg.get("pickle_model_fn")),
            weights_fp=_process_fp(cfg.get("weights_fn")),
            threshold_fp=_process_fp(cfg.get("threshold_fn")),
            importance_fp=_process_fp(cfg.get("importance_fn")),
            explainer_fp=_process_fp(cfg.get("explainer_fn")),
            one_hot_encode_fp=_process_fp(cfg.get("one_hot_encode_fn")),
            shap_type=cfg.get("shap_type"),
            training_size=cfg.get("training_size"),
            impute=cfg.get("impute", False),
            prefit_se=cfg.get("prefit_se", True),
        )"""


if __name__ == "__main__":
    if len(sys.argv) == 2:
        prepare_database(sys.argv[1])
    elif len(sys.argv) == 3:
        prepare_database(sys.argv[1], sys.argv[2])
    else:
        print("Invalid arguments. Usage: python preprocessing.py CONFIG_FILE [DIRECTORY]")
