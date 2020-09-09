import json
import os
import pickle
import random

import numpy as np
import pandas as pd
from mongoengine import connect
from pymongo import MongoClient
from sklearn.linear_model import Lasso

from sibyl.sibyl import global_explanation as ge
from sibyl.sibyl import local_feature_explanation as lfe
from sibylapp.db import schema
from sibylapp.db.utils import MappingsTransformer, ModelWrapperThresholds


def load_data(features, dataset_filepath):
    data = pd.read_csv(dataset_filepath)

    y = data.PRO_PLSM_NEXT730_DUMMY
    X = data[features]

    return X, y


def convert_to_categorical(X, mappings):
    cols = X.columns
    num_rows = X.shape[0]
    cat_cols = mappings['original_name'].values
    cat_data = {}
    for col in cols:
        if col not in cat_cols:
            cat_data[col] = X[col]
        if col in cat_cols:
            new_name = mappings[mappings['original_name'] == col]["name"].values[0]
            if new_name not in cat_data:
                cat_data[new_name] = np.empty(num_rows, dtype='object')
                # Handle a few specific cases
                if new_name == "PRI_FOCUS_GENDER":
                    cat_data[new_name] = np.full(num_rows, "Male", dtype='object')
                if new_name == "PRI_VICTIM_COUNT":
                    cat_data[new_name] = np.full(num_rows, "0")
            cat_data[new_name][np.where(X[col] == 1)] = \
                mappings[mappings['original_name'] == col]["value"].values[0]
    return pd.DataFrame(cat_data)


def insert_features(filepath):
    features_df = pd.read_csv(filepath)

    references = [schema.Category.find_one(name=cat) for cat in features_df['category']]
    features_df = features_df.drop('category', axis='columns')
    features_df['category'] = references

    items = features_df.to_dict(orient='records')
    schema.Feature.insert_many(items)
    return features_df["name"]


def insert_categories(filepath):
    cat_df = pd.read_csv(filepath)
    items = cat_df.to_dict(orient='records')
    schema.Category.insert_many(items)


def load_model_from_weights_sklearn(weights_filepath, model_base):
    """
    Load the model
    :return: (model, model features)
    """
    model_weights = pd.read_csv(weights_filepath)

    model = model_base
    dummy_X = np.zeros((1, model_weights.shape[1] - 1))
    dummy_y = np.zeros(model_weights.shape[1] - 1)
    model.fit(dummy_X, dummy_y)

    model.coef_ = np.array(model_weights["weight"][1:])
    model.intercept_ = model_weights["weight"][0]
    return model, model_weights["name"][1:]


def load_mappings_transformer(mappings_filepath, features):
    mappings = pd.read_csv(mappings_filepath)
    mappings = mappings[mappings["include"]]
    return MappingsTransformer(mappings, features)


def insert_model(model, transformer, set_doc, texts, importance_filepath=None, base_model=None,
                 explainer_filepath=None, features=None, dataset_filepath=None):
    def fit_explainer(base_model, transformer, dataset):
        explainer = lfe.fit_contribution_explainer(base_model, dataset.sample(100),
                                                   transformer=transformer, return_result=True,
                                                   use_linear_explainer=True)
        return explainer

    def get_importances(model, transformer, dataset, targets):
        importance_df = ge.get_global_importance(model, dataset[0:1000], targets[0:1000],
                                                 transformer=transformer)
        importance_df[importance_df < 0] = 0
        return importance_df

    model_serial = pickle.dumps(model)
    transformer_serial = pickle.dumps(transformer)
    name = texts["name"]
    description = texts["description"]
    performance = texts["performance"]

    dataset, targets = load_data(features, dataset_filepath)

    if importance_filepath is not None:
        importance_df = pd.read_csv(importance_filepath)
        importance_df = importance_df.set_index("name")
    else:
        importance_df = get_importances(base_model, transformer, dataset, targets)
    importances = importance_df.to_dict(orient='dict')["importance"]

    if explainer_filepath is not None:
        print("Loading explainer from file")
        with open(explainer_filepath, "rb") as f:
            explainer_serial = f.read()
    else:
        if features is None or dataset_filepath is None:
            print("Must have features and dataset to train explainer")
        explainer = fit_explainer(base_model, transformer, dataset)
        explainer_serial = pickle.dumps(explainer)

    items = {
        "model": model_serial,
        "transformer": transformer_serial,
        "name": name,
        "description": description,
        "performance": performance,
        "importances": importances,
        "explainer": explainer_serial,
        "training_set": set_doc
    }
    schema.Model.insert(**items)


def insert_entities(values_filepath, features_names, mappings_filepath=None,
                    counter_start=0, num=0, include_cases=False):
    values_df = pd.read_csv(values_filepath)[features_names + ["eid"]]
    if mappings_filepath is not None:
        mappings = pd.read_csv(mappings_filepath)
        mappings = mappings[mappings["include"]]
        values_df = convert_to_categorical(values_df, mappings)
    if num > 0:
        values_df = values_df.iloc[counter_start:num + counter_start]
    eids = values_df["eid"]

    cases = schema.Case.find()

    raw_entities = values_df.to_dict(orient="records")
    entities = []
    for raw_entity in raw_entities:
        entity = {}
        entity["eid"] = str(raw_entity["eid"])
        del raw_entity["eid"]
        entity["features"] = raw_entity
        if include_cases:
            entity["property"] = {"case_ids": [random.choice(cases).case_id]}
        entities.append(entity)
    schema.Entity.insert_many(entities)
    return eids


def insert_training_set(eids):
    references = [schema.Entity.find_one(eid=str(eid)) for eid in eids]
    training_set = {"entities": references}

    set_doc = schema.TrainingSet.insert(**training_set)
    return set_doc


def insert_cases(filepath):
    case_df = pd.read_csv(filepath)
    items_raw = case_df.to_dict(orient='records')
    items = []
    for item_raw in items_raw:
        item = {"case_id": str(item_raw["case_id"]),
                "property": {"team": item_raw["team"]}}
        items.append(item)
    schema.Case.insert_many(items)


def generate_feature_distribution_doc(save_path, model, transformer,
                                      dataset_filepath, features_filepath):
    features = pd.read_csv(features_filepath)
    feature_names = features["name"].append(pd.Series(["PRO_PLSM_NEXT365_DUMMY",
                                                       "PRO_PLSM_NEXT730_DUMMY"]))
    dataset, targets = load_data(feature_names, dataset_filepath)

    boolean_features = features[features['type'].isin(['binary', 'categorical'])]["name"]
    boolean_features = boolean_features.append(pd.Series(["PRO_PLSM_NEXT365_DUMMY",
                                                          "PRO_PLSM_NEXT730_DUMMY"]))
    dataset_cat = dataset[boolean_features]

    numeric_features = features[features['type'] == 'numeric']["name"]
    dataset_num = dataset[numeric_features]

    summary_dict = {}
    for output in range(1, 21):
        row_details = {}
        rows = ge.get_rows_by_output(output, model.predict, dataset, row_labels=None,
                                     transformer=transformer)

        count_total = len(rows)
        count_removed = sum(targets.iloc[rows])
        row_details["total cases"] = count_total
        row_details["total removed"] = count_removed

        cat_summary = ge.summary_categorical(dataset_cat.iloc[rows].applymap(str))
        num_summary = ge.summary_numeric(dataset_num.iloc[rows])

        distributions = {}
        for (i, name) in enumerate(boolean_features):
            distributions[name] = {"type": "categorical", "metrics": [cat_summary[0][i].tolist(),
                                                                      cat_summary[1][i].tolist()]}
        for (i, name) in enumerate(numeric_features):
            distributions[name] = {"type": "numeric", "metrics": num_summary[i]}
        row_details["distributions"] = distributions

        summary_dict[output] = row_details

    with open(save_path, 'w') as f:
        json.dump(summary_dict, f, indent=4, sort_keys=True)


def test_validation():
    pass


if __name__ == "__main__":
    # CONFIGURATIONS
    include_database = False
    client = MongoClient("localhost", 27017)
    connect('sibylapp', host='localhost', port=27017)
    directory = "data"

    # INSERT CATEGORIES
    insert_categories(os.path.join(directory, "categories.csv"))

    # INSERT FEATURES
    feature_names = insert_features(os.path.join(directory, "agg_features.csv")).tolist()

    # INSERT CASES
    insert_cases(os.path.join(directory, "cases.csv"))

    # INSERT ENTITIES
    eids = insert_entities(os.path.join(directory, "agg_true_entities.csv"), feature_names,
                           mappings_filepath=os.path.join(directory, "mappings.csv"),
                           include_cases=True)

    # INSERT FULL DATASET
    if include_database:
        eids = insert_entities(os.path.join(directory, "agg_dataset.csv"), feature_names,
                               counter_start=17, num=100000)
    set_doc = insert_training_set(eids)

    # INSERT MODEL
    thresholds = [0.01174609, 0.01857239, 0.0241622, 0.0293587,
                  0.03448975, 0.0396932, 0.04531139, 0.051446,
                  0.05834176, 0.06616039, 0.07549515, 0.08624243,
                  0.09912388, 0.11433409, 0.13370343, 0.15944484,
                  0.19579651, 0.25432879, 0.36464856, 1.0]
    base_model, model_features = load_model_from_weights_sklearn(
        os.path.join(directory, "weights.csv"), Lasso())
    model = ModelWrapperThresholds(base_model, thresholds, features=model_features)
    transformer = load_mappings_transformer(os.path.join(directory, "mappings.csv"), model_features)

    with open(os.path.join(directory, "description.txt"), 'r') as file:
        description = file.read()
    with open(os.path.join(directory, "performance.txt"), 'r') as file:
        performance = file.read()
    texts = {
        "name": "Lasso Regression Model",
        "description": description,
        "performance": performance
    }

    insert_model(model, transformer, set_doc, texts,
                 dataset_filepath=os.path.join(directory, "agg_dataset.csv"),
                 base_model=base_model, features=feature_names)

    # PRE-COMPUTE DISTRIBUTION INFORMATION
    generate_feature_distribution_doc("precomputed/agg_distributions.json", model, transformer,
                                      os.path.join(directory, "agg_dataset.csv"),
                                      os.path.join(directory, "agg_features.csv"))
    test_validation()
