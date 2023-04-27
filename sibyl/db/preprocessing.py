import json
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

import sibyl.global_explanation as ge
from sibyl.db import schema
from sibyl.db.utils import ModelWrapperThresholds
from sibyl.utils import get_project_root


def _process_fp(fn):
    if fn is not None:
        return os.path.join(directory, fn)
    return None


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


def insert_terms(filepath):
    context_df = pd.read_csv(filepath)
    items = dict(zip(context_df["key"], context_df["term"]))
    context_dict = {"terms": items}
    schema.Context.insert(**context_dict)


def insert_entities(
    feature_values_filepath,
    features_names,
    pre_transformers_fp=None,
    one_hot_decode_fp=None,
    impute=False,
    num=None,
):
    values_df = pd.read_csv(feature_values_filepath)[features_names + ["eid"]]
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

    # TODO: add groups to entities
    # groups = schema.EntityGroup.find()

    raw_entities = values_df.to_dict(orient="records")
    entities = []
    for raw_entity in raw_entities:
        entity = {}
        entity["eid"] = str(raw_entity["eid"])
        del raw_entity["eid"]
        entity["features"] = raw_entity
        entities.append(entity)
    schema.Entity.insert_many(entities)
    return eids


def insert_training_set(eids):
    references = [schema.Entity.find_one(eid=str(eid)) for eid in eids]
    training_set = {"entities": references}

    set_doc = schema.TrainingSet.insert(**training_set)
    return set_doc


def insert_model(
    features,
    dataset_fp,
    target,
    pickle_model_fp=None,
    weights_fp=None,
    threshold_fp=None,
    one_hot_encode_fp=None,
    model_transformers_fp=None,
    importance_fp=None,
    explainer_fp=None,
    shap_type=None,
    training_size=None
):
    model_features = features

    # Base model options
    if pickle_model_fp is not None:
        # Load from pickle file
        print("Loading model from pickle file.")
        model = pickle.load(open(pickle_model_fp, "rb"))
    elif weights_fp is not None:
        # Load from list of weights
        print("Loading model from weights")
        model, model_features = _load_model_from_weights_sklearn(weights_fp, LinearRegression())
    else:
        raise ValueError("Must provide at least one model format")

    # Model wrapping options
    if threshold_fp is not None:
        # Bin output based on thresholds
        threshold_df = pd.read_csv(threshold_fp)
        thresholds = threshold_df["thresholds"].tolist()
        model = ModelWrapperThresholds(model, thresholds, features=model_features)

    transformers = []

    if one_hot_encode_fp is not None:
        mappings = pd.read_csv(one_hot_encode_fp)
        if "include" in mappings:
            mappings = mappings[mappings["include"]]
        transformer = MappingsOneHotEncoder(Mappings.generate_mappings(dataframe=mappings))
        transformers.append(transformer)

    if model_transformers_fp is not None:
        transformers = pickle.load(open(model_transformers_fp, "rb"))

    train_dataset, targets = _load_data(features, dataset_fp, target)

    model_serial = pickle.dumps(model)

    texts = {
        "name": "placeholder",
        "description": "placeholder",
        "performance": "placeholder",
    }
    name = texts["name"]
    description = texts["description"]
    performance = texts["performance"]

    if explainer_fp is not None:
        print("Loading explainer from file")
        with open(explainer_fp, "rb") as f:
            explainer_serial = f.read()
            explainer = pickle.loads(explainer_serial)
    else:
        # TODO: add additional explainers/allow for multiple algorithms
        explainer = RealApp(model, transformers=transformers)
        explainer.prepare_feature_contributions(
            model_id=0, shap_type=shap_type, x_train_orig=train_dataset, y_train=targets,
            training_size=training_size
        )
        explainer.prepare_feature_importance(
            model_id=0, shap_type=shap_type, x_train_orig=train_dataset, y_train=targets,
            training_size=training_size
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
        importance_df = importance_df.rename(columns={"Feature Name": "name", "Importance": "importance"})
        importance_df.set_index("name")

    importances = importance_df.to_dict(orient="dict")["importance"]

    items = {
        "model": model_serial,
        "name": name,
        "description": description,
        "performance": performance,
        "importances": importances,
        "explainer": explainer_serial,
        "training_set": set_doc,
    }
    schema.Model.insert(**items)
    return explainer


def generate_feature_distribution_doc(
    save_path, explainer, target, dataset_filepath, features_filepath
):
    features = pd.read_csv(features_filepath)
    feature_names = features["name"]
    dataset, targets = _load_data(feature_names, dataset_filepath, target)

    boolean_features = features[features["type"].isin(["binary", "categorical"])]["name"]
    dataset_cat = dataset[boolean_features]

    numeric_features = features[features["type"] == "numeric"]["name"]
    dataset_num = dataset[numeric_features]

    summary_dict = {}
    # TODO: generalize list of outputs
    for output in range(1, 21):
        row_details = {}
        rows = ge.get_rows_by_output(output, explainer.model_predict, dataset, row_labels=None)

        count_total = len(rows)

        count_removed = sum(targets.iloc[rows])
        row_details["total cases"] = count_total
        row_details["total removed"] = count_removed

        cat_summary = ge.summary_categorical(dataset_cat.iloc[rows].applymap(str))
        num_summary = ge.summary_numeric(dataset_num.iloc[rows])

        distributions = {}
        for i, name in enumerate(boolean_features):
            distributions[name] = {
                "type": "categorical",
                "metrics": [cat_summary[0][i].tolist(), cat_summary[1][i].tolist()],
            }
        for i, name in enumerate(numeric_features):
            distributions[name] = {"type": "numeric", "metrics": num_summary[i]}
        row_details["distributions"] = distributions

        summary_dict[output] = row_details

    with open(save_path, "w") as f:
        json.dump(summary_dict, f, indent=4, sort_keys=True)


if __name__ == "__main__":
    config_file = sys.argv[1]
    with open(config_file, "r") as f:
        cfg = yaml.safe_load(f)

    # Begin database loading ---------------------------
    client = MongoClient("localhost", 27017)
    database_name = cfg["database_name"]
    if cfg.get("directory") is None:
        directory = os.path.join(get_project_root(), "dbdata", database_name)
    else:
        directory = os.path.join(get_project_root(), "dbdata", cfg["directory"])

    if cfg.get("DROP_OLD", False):
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
    insert_terms(os.path.join(directory, "terms.csv"))

    # INSERT ENTITIES
    eids = insert_entities(
        os.path.join(directory, "entities.csv"),
        feature_names,
        pre_transformers_fp=_process_fp(cfg.get("pre_transformers_fn")),
        one_hot_decode_fp=_process_fp(cfg.get("one_hot_decode_fn")),
        impute=cfg.get("impute", False),
    )

    # INSERT FULL DATASET
    dataset_fp = _process_fp(cfg.get("dataset_fn"))
    if cfg.get("include_database", False) and os.path.exists(dataset_fp):
        eids = insert_entities(dataset_fp, feature_names, num=cfg.get("num_from_database"))
    set_doc = insert_training_set(eids)

    # INSERT MODEL
    target = cfg.get("target")
    explainer = insert_model(
        feature_names,
        dataset_fp,
        target,
        pickle_model_fp=_process_fp(cfg.get("pickle_model_fn")),
        weights_fp=_process_fp(cfg.get("weights_fn")),
        threshold_fp=_process_fp(cfg.get("threshold_fn")),
        importance_fp=_process_fp(cfg.get("importance_fn")),
        explainer_fp=_process_fp(cfg.get("explainer_fn")),
        one_hot_encode_fp=_process_fp(cfg.get("one_hot_encode_fn")),
        shap_type=cfg.get("shap_type"),
        training_size=cfg.get("training_size")
    )

    # PRE-COMPUTE DISTRIBUTION INFORMATION
    # generate_feature_distribution_doc("precomputed/agg_distributions.json", explainer, target,
    #                                   dataset_fp, os.path.join(directory, "features.csv"))
    # test_validation()
