import os
import pickle
import random

import numpy as np
import pandas as pd
from mongoengine import connect
from pymongo import MongoClient
from pyreal.explainers import LocalFeatureContribution, GlobalFeatureImportance

from pyreal.transformers import MultiTypeImputer

from sibyl.db import schema
from sibyl.db.utils import MappingsTransformer


def make_compatible(s):
    return s.replace(".", "_")


def load_data(features, dataset_filepath):
    data = pd.read_csv(dataset_filepath)

    y = data.label
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


def insert_model(features, model_filepath, dataset_filepath,
                 importance_filepath=None, explainer_filepath=None):
    model = pickle.load(open(model_filepath, "rb"))

    dataset, targets = load_data(features, dataset_filepath)

    model_serial = pickle.dumps(model)
    transformer = MultiTypeImputer()
    transformer.fit(dataset)
    dataset = transformer.transform(dataset)
    transformer_serial = pickle.dumps(transformer)

    texts = {
        "name": "Model",
        "description": "placeholder",
        "performance": "placeholder"
    }
    name = texts["name"]
    description = texts["description"]
    performance = texts["performance"]

    if importance_filepath is not None:
        importance_df = pd.read_csv(importance_filepath)
        importance_df = importance_df.set_index("name")
    else:
        global_explainer = GlobalFeatureImportance(model, dataset.sample(1000), fit_on_init=True)
        importance_df = global_explainer.produce().T
        importance_df.columns = ["importance"]
        importance_df.to_csv("importances.csv")
        #raise NotImplementedError()

    importances = importance_df.to_dict(orient='dict')["importance"]

    if explainer_filepath is not None:
        print("Loading explainer from file")
        with open(explainer_filepath, "rb") as f:
            explainer_serial = f.read()
    else:
        explainer = LocalFeatureContribution(model, dataset.sample(100),
                                             e_algorithm="shap",
                                             fit_on_init=True)
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
                    counter_start=0, num=0, include_referrals=False):
    values_df = pd.read_csv(values_filepath)[features_names + ["eid"]]
    transformer = MultiTypeImputer()
    transformer.fit(values_df)
    values_df = transformer.transform(values_df)
    values_df["eid"] = values_df["eid"].astype(int)

    if mappings_filepath is not None:
        mappings = pd.read_csv(mappings_filepath)
        mappings = mappings[mappings["include"]]
        values_df = convert_to_categorical(values_df, mappings)
    if num > 0:
        values_df = values_df.iloc[counter_start:num + counter_start]
    eids = values_df["eid"]

    referrals = schema.Referral.find()

    raw_entities = values_df.to_dict(orient="records")
    entities = []
    for raw_entity in raw_entities:
        entity = {}
        entity["eid"] = str(raw_entity["eid"])
        del raw_entity["eid"]
        entity["features"] = raw_entity
        if include_referrals:
            entity["property"] = {"referral_ids": [random.choice(referrals).referral_id]}
        entities.append(entity)
    schema.Entity.insert_many(entities)
    return eids


def insert_training_set(eids):
    references = [schema.Entity.find_one(eid=str(eid)) for eid in eids]
    training_set = {"entities": references}

    set_doc = schema.TrainingSet.insert(**training_set)
    return set_doc


def insert_referrals(filepath):
    referral_df = pd.read_csv(filepath)
    items_raw = referral_df.to_dict(orient='records')
    items = []
    for item_raw in items_raw:
        item = {"referral_id": str(item_raw["referral_id"]),
                "property": {"team": item_raw["team"]}}
        items.append(item)
    schema.Referral.insert_many(items)


def test_validation():
    pass


if __name__ == "__main__":
    # CONFIGURATIONS
    include_database = False
    client = MongoClient("localhost", 27017)
    connect('iberdrola', host='localhost', port=27017)
    directory = os.path.join("..", "..", "..", "..", "..", "OneDrive", "Documents", "Research", "Sibyl", "data", "wind-turbines")

    # INSERT CATEGORIES
    insert_categories(os.path.join(directory, "categories.csv"))

    # INSERT FEATURES
    feature_names = insert_features(os.path.join(directory, "features.csv")).tolist()

    # INSERT ENTITIES
    eids = insert_entities(os.path.join(directory, "data2.csv"), feature_names,
                           include_referrals=False)

    set_doc = insert_training_set(eids)

    # INSERT MODEL
    model_filepath = os.path.join(directory, "model.pkl")
    dataset_filepath = os.path.join(directory, "data2.csv")
    importance_filepath = os.path.join(directory, "importances.csv")

    insert_model(features=feature_names, model_filepath=model_filepath,
                 dataset_filepath=dataset_filepath, importance_filepath=importance_filepath)