import os
import pickle
import random

import numpy as np
import pandas as pd
from mongoengine import connect
from pymongo import MongoClient
from sklearn.linear_model import Lasso

from sibylapp.db import schema
from sibylapp.db.utils import ModelWrapper


def insert_features(filepath):
    features_df = pd.read_csv(filepath)

    references = [schema.Category.find_one(name=cat) for cat in features_df['category']]
    features_df.drop('category', axis='columns')
    features_df['category'] = references

    items = features_df.to_dict(orient='records')
    schema.Feature.insert_many(items)


def insert_categories(filepath):
    cat_df = pd.read_csv(filepath)
    items = cat_df.to_dict(orient='records')
    schema.Category.insert_many(items)


def insert_model(model_filepath, importance_filepath,
                 explainer_filepath, set_doc):
    def load_model(model_filepath):
        """
        Load the model
        :return: the model
        """
        model_weights = pd.read_csv(model_filepath)

        model = Lasso()
        dummy_X = np.zeros((1, model_weights.shape[1] - 1))
        dummy_y = np.zeros(model_weights.shape[1] - 1)
        model.fit(dummy_X, dummy_y)

        model.coef_ = np.array(model_weights["weight"][1:])
        model.intercept_ = model_weights["weight"][0]
        return model, model_weights["name"][model_weights["name"] != "(Intercept)"]

    base_model, features = load_model(model_filepath)
    model = ModelWrapper(base_model, features)

    model_serial = pickle.dumps(model)

    name = "Test Model 1"
    description = "A basic lasso regression model.\n " \
                  "Works by multiplying features by weights"
    performance = "98.7% accurate"

    importance_df = pd.read_csv(importance_filepath)
    importance_df = importance_df.set_index("name")
    importances = importance_df.to_dict(orient='dict')["importance"]

    with open(explainer_filepath, "rb") as f:
        explainer = f.read()
    items = {
        "model": model_serial,
        "name": name,
        "description": description,
        "performance": performance,
        "importances": importances,
        "explainer": explainer,
        "training_set": set_doc
    }
    schema.Model.insert(**items)


def insert_entities(values_filepath, weights_filepath,
                    counter_start=0, num=0, include_cases=False):
    model_weights = pd.read_csv(weights_filepath)
    features = model_weights["name"][model_weights["name"] != "(Intercept)"].tolist()

    feature_df = pd.read_csv(values_filepath)[features + ["eid"]]
    if num > 0:
        feature_df = feature_df.iloc[counter_start:num + counter_start]
    eids = feature_df["eid"]

    cases = schema.Case.find()

    raw_entities = feature_df.to_dict(orient="records")
    entities = []
    for raw_entity in raw_entities:
        entity = {}
        entity["eid"] = str(raw_entity["eid"])
        del raw_entity["eid"]
        entity["features"] = raw_entity
        if include_cases:
            entity["property"] = {"case_id": [random.choice(cases).case_id]}
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


def test_validation():
    pass


if __name__ == "__main__":
    client = MongoClient("localhost", 27017)
    connect('sibylapp', host='localhost', port=27017)

    directory = "data"

    insert_cases(os.path.join(directory, "cases.csv"))

    eids = insert_entities(os.path.join(directory, "entity_features.csv"),
                           os.path.join(directory, "weights.csv"),
                           include_cases=True)
    # eids = insert_entities(os.path.join(directory, "dataset.csv"),
    #                       os.path.join(directory, "weights.csv"),
    #                       counter_start=17, num=100000)
    set_doc = insert_training_set(eids)
    insert_categories(os.path.join(directory, "categories.csv"))
    insert_features(os.path.join(directory, "features.csv"))
    insert_model(model_filepath=os.path.join(directory, "weights.csv"),
                 importance_filepath=os.path.join(directory, "importances.csv"),
                 explainer_filepath=os.path.join(directory, "explainer"),
                 set_doc=set_doc)
    test_validation()
