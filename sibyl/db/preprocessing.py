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
from tqdm import tqdm

from sibyl.db import schema
from sibyl.db.utils import ModelWrapperThresholds
from sibyl.utils import get_project_root


def _load_data(training_entity_filepath, target):
    try:
        data = pd.read_csv(training_entity_filepath)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Dataset file {training_entity_filepath} not found. Must provide valid file."
        )

    y = data[target]
    X = data.drop(target, axis="columns")

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


def insert_features(filepath):
    try:
        features_df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Features file {filepath} not found. Must provide valid features file"
        )
    if "category" in features_df:
        categories = set(features_df["category"])
        already_inserted_categories = schema.Category.find(as_df_=True, only_=["name"])
        if not already_inserted_categories.empty:
            already_inserted_categories = set(already_inserted_categories["name"])
        schema.Category.insert_many(
            [{"name": cat} for cat in categories if cat not in already_inserted_categories]
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

    if "output_preset" in context_config:
        with open(os.path.join(get_project_root(), "sibyl", "db", "output_presets.yml"), "r") as f:
            output_preset_dict = yaml.safe_load(f)
        if context_config["output_preset"] in output_preset_dict:
            config_values = output_preset_dict[context_config["output_preset"]]
            for config_name in config_values:
                if config_name not in output_preset_dict:
                    context_config[config_name] = config_values[config_name]

    schema.Context.insert(config=context_config)


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
        if pbar is not None:
            pbar.update(total_time / len(raw_entities))
    schema.Entity.insert_many(entities)
    return eids, use_rows


def insert_training_set(eids, target):
    references = [schema.Entity.find_one(eid=str(eid)) for eid in eids]
    training_set = {"entities": references, "target": target}

    set_doc = schema.TrainingSet.insert(**training_set)
    return set_doc


def insert_model(
    training_data_fp,
    target,
    set_doc,
    explainer_fp,
    model_id=None,
    training_size=None,
    fit_explainers=False,
    fit_se=True,
):
    description = "placeholder"
    performance = "placeholder"
    if model_id is None:
        model_id = "model"

    try:
        with open(explainer_fp, "rb") as f:
            explainer_serial = f.read()
            explainer = pickle.loads(explainer_serial)
            explainer.id_column = "eid"
    except FileNotFoundError:
        raise FileNotFoundError(f"Explainer file {explainer_fp} not found. ")

    train_dataset, targets = _load_data(training_data_fp, target)

    if fit_explainers:
        explainer.prepare_feature_contributions(
            x_train_orig=train_dataset,
            y_train=targets,
            training_size=training_size,
        )
        explainer.prepare_feature_importance(
            model_id=0,
            x_train_orig=train_dataset,
            y_train=targets,
            training_size=training_size,
        )
        if fit_se:
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

    importance_dict = explainer.produce_feature_importance()
    importance_df = pd.DataFrame.from_dict(importance_dict)
    importance_df = importance_df.rename(
        columns={"Feature Name": "name", "Importance": "importance"}
    )
    importance_df.set_index("name")

    importances = importance_df.to_dict(orient="dict")["importance"]

    items = {
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
        "Model": 20,
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
    insert_categories(_process_fp(cfg.get("category_fn")))
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

    # INSERT MODEL
    if cfg.get("explainer_directory_name"):
        explainer_directory = _process_fp(cfg.get("explainer_directory_name"))
        if not os.path.isdir(explainer_directory):
            raise FileNotFoundError(
                f"Explainer directory {explainer_directory} is not a valid directory."
            )
        number_of_explainers = len(os.listdir(explainer_directory))
        for i, explainer_file in enumerate(os.listdir(explainer_directory)):
            if explainer_file.endswith(".pkl"):  # Ignore other files in the directory
                insert_model(
                    _process_fp(
                        cfg.get("training_entities_fn") or cfg.get("entity_fn") or "entities.csv"
                    ),
                    cfg.get("target", "target"),
                    set_doc,
                    explainer_fp=os.path.join(explainer_directory, explainer_file),
                    model_id=explainer_file[:-4],
                    training_size=cfg.get("training_size"),
                    fit_explainers=cfg.get("fit_explainers", False),
                    fit_se=cfg.get("fit_se", True),
                )
            pbar.update(times["Model"] / number_of_explainers)
    else:
        pbar.set_description("Inserting model...")
        insert_model(
            _process_fp(cfg.get("training_entities_fn") or cfg.get("entity_fn") or "entities.csv"),
            cfg.get("target", "target"),
            set_doc,
            explainer_fp=_process_fp(cfg.get("explainer_fn")),
            model_id=cfg.get("model_name"),
            training_size=cfg.get("training_size"),
            fit_explainers=cfg.get("fit_explainers", False),
            fit_se=cfg.get("fit_se", True),
        )
        pbar.update(times["Model"])


if __name__ == "__main__":
    if len(sys.argv) == 2:
        prepare_database(sys.argv[1])
    elif len(sys.argv) == 3:
        prepare_database(sys.argv[1], sys.argv[2])
    else:
        print("Invalid arguments. Usage: python preprocessing.py CONFIG_FILE [DIRECTORY]")
