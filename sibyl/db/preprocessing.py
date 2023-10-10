import os
import pickle
import sys

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
    features_df = pd.read_csv(filepath)

    if "category" in features_df:
        references = [schema.Category.find_one(name=cat) for cat in features_df["category"]]
        features_df = features_df.drop("category", axis="columns")
        features_df["category"] = references

    items = features_df.to_dict(orient="records")
    schema.Feature.insert_many(items)
    return features_df["name"].tolist()


def insert_categories(filepath):
    cat_df = pd.read_csv(filepath)
    items = cat_df.to_dict(orient="records")
    schema.Category.insert_many(items)


def insert_entity_groups(filepath):
    group_df = pd.read_csv(filepath)
    items_raw = group_df.to_dict(orient="records")
    items = []
    for item_raw in items_raw:
        properties = {key: val for key, val in item_raw.items() if key != "group_id"}
        item = {"group_id": str(item_raw["group_id"]), "property": properties}
        items.append(item)
    schema.EntityGroup.insert_many(items)


def insert_context(terms_fp, gui_preset, gui_config):
    def set_config(config_values):
        for config_name in config_values:
            if config_name not in gui_config:
                gui_config[config_name] = config_values[config_name]

    terms_df = pd.read_csv(terms_fp)
    items = dict(zip(terms_df["key"], terms_df["term"]))
    if gui_config is None:
        gui_config = {}
    with open(os.path.join(get_project_root(), "sibyl", "db", "gui_presets.yml"), "r") as f:
        gui_preset_dict = yaml.safe_load(f)
    if gui_preset in gui_preset_dict:
        set_config(gui_preset_dict[gui_preset])
    context_dict = {"terms": items, "gui_config": gui_config, "gui_preset": gui_preset}
    schema.Context.insert(**context_dict)


def insert_entities(
    feature_values_filepath,
    features_names,
    target=None,
    pre_transformers_fp=None,
    one_hot_decode_fp=None,
    impute=False,
    num=None,
):
    values_df = pd.read_csv(feature_values_filepath)
    features_to_extract = ["eid"] + features_names
    if "row_id" in values_df:
        features_to_extract = features_to_extract + ["row_id"]
    if target in values_df:
        features_to_extract += [target]
    values_df = values_df[features_to_extract]
    transformers = []
    if impute is not None and impute:
        transformer = MultiTypeImputer()
        transformer.fit(values_df)
        transformers.append(transformer)
    if one_hot_decode_fp is not None:
        # Mappings from one-hot encoded columns to categorical data
        mappings = pd.read_csv(one_hot_decode_fp)
        if "include" in mappings:
            mappings = mappings[mappings["include"]]
        transformer = MappingsOneHotDecoder(Mappings.generate_mappings(dataframe=mappings))
        transformers.append(transformer)
    if pre_transformers_fp is not None:
        transformers = pickle.load(open(pre_transformers_fp, "rb"))
    values_df = run_transformers(transformers, values_df)

    if num is not None:
        values_df = values_df.sample(num, random_state=100)
    eids = values_df["eid"]
    values_df = values_df.copy()  # Fixing fragmentation if transforming resulted in any

    # TODO: add groups to entities
    # groups = schema.EntityGroup.find()

    if "row_id" not in values_df:
        values_df["row_id"] = pd.Series(np.arange(0, values_df.shape[0])).astype(str)
    else:
        values_df["row_id"] = values_df["row_id"].astype(str)
    values_df = values_df.copy()
    values_df = values_df.set_index(["eid", "row_id"])
    raw_entities = {
        level: values_df.xs(level).to_dict("index") for level in values_df.index.levels[0]
    }
    entities = []
    for eid in raw_entities:
        entity = {"eid": str(eid), "row_ids": list(raw_entities[eid].keys())}
        targets = {}
        for row_id in raw_entities[eid]:
            if target in raw_entities[eid][row_id]:
                targets[row_id] = raw_entities[eid][row_id].pop(target)
        entity["features"] = raw_entities[eid]
        entity["labels"] = targets
        entities.append(entity)
    schema.Entity.insert_many(entities)
    return eids


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
    name=None,
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
    if name is None:
        name = "model"

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
        "name": name,
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
    if os.path.exists(os.path.join(directory, "categories.csv")):
        insert_categories(os.path.join(directory, "categories.csv"))

    # INSERT FEATURES
    feature_names = insert_features(os.path.join(directory, "features.csv"))

    # INSERT ENTITY GROUPS
    if os.path.exists(os.path.join(directory, "groups.csv")):
        insert_entity_groups(os.path.join(directory, "groups.csv"))

    # INSERT CONTEXT
    insert_context(
        os.path.join(directory, "terms.csv"), cfg.get("gui_preset"), cfg.get("gui_config")
    )

    # INSERT ENTITIES
    eids = insert_entities(
        os.path.join(directory, "entities.csv"),
        feature_names,
        target=cfg.get("target"),
        pre_transformers_fp=_process_fp(cfg.get("pre_transformers_fn")),
        one_hot_decode_fp=_process_fp(cfg.get("one_hot_decode_fn")),
        impute=cfg.get("impute", False),
    )

    # INSERT FULL DATASET
    dataset_fp = _process_fp(cfg.get("dataset_fn"))
    if cfg.get("include_database", False) and os.path.exists(dataset_fp):
        eids = insert_entities(
            dataset_fp, feature_names, target=cfg.get("target"), num=cfg.get("num_from_database")
        )
    target = cfg.get("target")
    set_doc = insert_training_set(eids, target)

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
                    name=explainer_file[:-4],  # remove .pkl
                    pickle_model_fp=_process_fp(cfg.get("pickle_model_fn")),
                    importance_fp=_process_fp(cfg.get("importance_fn")),
                    explainer_fp=os.path.join(explainer_directory, explainer_file),
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
        )


if __name__ == "__main__":
    if len(sys.argv) == 2:
        prepare_database(sys.argv[1])
    elif len(sys.argv) == 3:
        prepare_database(sys.argv[1], sys.argv[2])
    else:
        print("Invalid arguments. Usage: python preprocessing.py CONFIG_FILE [DIRECTORY]")
