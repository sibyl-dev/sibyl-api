import json
import os
import pickle
import random

import numpy as np
import pandas as pd
from mongoengine import connect
from pymongo import MongoClient
from pyreal.explainers import LocalFeatureContribution
from sklearn.linear_model import Lasso

import sibyl.global_explanation as ge
from sibyl.db import schema
from sibyl.db.utils import MappingsTransformer, ModelWrapperThresholds


def insert_features(filepath):
    features_df = pd.read_csv(filepath)
    print(features_df.head)

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


def load_mappings_transformer(mappings_filepath, features):
    mappings = pd.read_csv(mappings_filepath)
    mappings = mappings[mappings["include"]]
    return MappingsTransformer(mappings, features)


def insert_model(model_filepath, explainer_filepath):
    with open(model_filepath, "rb") as f:
        model_serial = f.read()

    texts = {
        "name": "Lasso Regression Model",
        "description": "placeholder",
        "performance": "placeholder"
    }
    name = texts["name"]
    description = texts["description"]
    performance = texts["performance"]

    if explainer_filepath is not None:
        print("Loading explainer from file")
        with open(explainer_filepath, "rb") as f:
            explainer_serial = f.read()

   # with open(transformer_filepath, "rb") as f:
   #     transformer_serial = f.read()


    items = {
        "model": model_serial,
        "name": name,
        "description": description,
        "performance": performance,
        "explainer": explainer_serial,
        "training_set": set_doc
    }
    schema.Model.insert(**items)


def insert_entities(values_filepath, features_names,
                    include_referrals=False):
    values_df = pd.read_csv(values_filepath)[features_names + ["eid"]]
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


def test_validation():
    pass


if __name__ == "__main__":
    # CONFIGURATIONS
    include_database = False
    client = MongoClient("localhost", 27017)
    connect('housing', host='localhost', port=27017)
    #directory = os.path.join("..", "..", "..", "sibyl-data", "housing")
    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "housing")

    # INSERT CATEGORIES
    insert_categories(os.path.join(directory, "categories.csv"))

    # INSERT FEATURES
    feature_names = insert_features(os.path.join(directory, "features.csv")).tolist()

    # INSERT ENTITIES
    eids = insert_entities(os.path.join(directory, "entities.csv"), feature_names,
                           include_referrals=False)

    set_doc = insert_training_set(eids)

    # INSERT MODEL
    model_filepath = os.path.join(directory, "model.pkl")
    explainer_filepath = os.path.join(directory, "explainer.pkl")

    insert_model(model_filepath=model_filepath,
                 explainer_filepath=explainer_filepath)

    # PRE-COMPUTE DISTRIBUTION INFORMATION
    '''generate_feature_distribution_doc("precomputed/agg_distributions.json", model, transformer,
                                      os.path.join(directory, "agg_dataset.csv"),
                                      os.path.join(directory, "agg_features.csv"))'''
    test_validation()
