import json
import os
import pickle
import random
import sys

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

    if 'category' in features_df:
        references = [schema.Category.find_one(name=cat) for cat in features_df['category']]
        features_df = features_df.drop('category', axis='columns')
        features_df['category'] = references

    items = features_df.to_dict(orient='records')
    schema.Feature.insert_many(items)
    return features_df["name"].tolist()


def insert_categories(filepath):
    cat_df = pd.read_csv(filepath)
    items = cat_df.to_dict(orient='records')
    schema.Category.insert_many(items)


def insert_entity_groups(filepath):
    group_df = pd.read_csv(filepath)
    items_raw = group_df.to_dict(orient='records')
    items = []
    for item_raw in items_raw:
        properties = {key: val for key, val in item_raw.items() if key != 'group_id'}
        item = {"group_id": str(item_raw["group_id"]),
                "property": properties}
        items.append(item)
    schema.EntityGroup.insert_many(items)


def insert_terms(filepath):
    context_df = pd.read_csv(filepath)
    items = dict(zip(context_df["key"], context_df["term"]))
    context_dict = {"terms": items}
    schema.Context.insert(**context_dict)


def insert_entities(feature_values_filepath, features_names, mappings_filepath=None,
                    counter_start=0, num=0):
    values_df = pd.read_csv(feature_values_filepath)[features_names + ["eid"]]
    # Mappings from one-hot encoded columns to categorical data
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


if __name__ == "__main__":
    DROP_OLD = True

    database_name = sys.argv[1]
    directory = os.path.join("..", "..", "dbdata", sys.argv[2])

    # CONFIGURATIONS
    include_database = False
    client = MongoClient("localhost", 27017)

    if DROP_OLD:
        client.drop_database(database_name)
    connect(database_name, host='localhost', port=27017)

    # INSERT CATEGORIES, IF PROVIDED
    if os.path.exists(os.path.join(directory, "categories.csv")):
        insert_categories(os.path.join(directory, "categories.csv"))

    # INSERT FEATURES
    feature_names = insert_features(os.path.join(directory, "features.csv")).tolist()
'''
    # INSERT REFERRALS
    insert_referrals(os.path.join(directory, "referrals.csv"))

    # INSERT CONTEXT
    insert_terms(os.path.join(directory, "terms.csv"))

    # INSERT ENTITIES
    eids = insert_entities(os.path.join(directory, "entities.csv"), feature_names,
                           mappings_filepath=os.path.join(directory, "mappings.csv"))

'''
    # INSERT FULL DATASET
    if include_database:
        eids = insert_entities(os.path.join(directory, "dataset.csv"), feature_names,
                               counter_start=17, num=100000)
    set_doc = insert_training_set(eids)

    # INSERT MODEL
    model_filepath = os.path.join(directory, "weights.csv")
    dataset_filepath = os.path.join(directory, "dataset.csv")
    importance_filepath = os.path.join(directory, "importances.csv")

    insert_model(features=feature_names, model_filepath=model_filepath,
                 dataset_filepath=dataset_filepath, importance_filepath=importance_filepath)

    # PRE-COMPUTE DISTRIBUTION INFORMATION
    generate_feature_distribution_doc("precomputed/agg_distributions.json", model, transformer,
                                      os.path.join(directory, "agg_dataset.csv"),
                                      os.path.join(directory, "agg_features.csv"))
    test_validation()
