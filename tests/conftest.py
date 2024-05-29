import datetime
import pickle

import numpy as np
import pandas as pd
import pytest
from mongoengine import connect
from mongoengine.connection import disconnect
from pymongo import MongoClient
from pyreal import RealApp
from pyreal.transformers import FeatureSelectTransformer
from sklearn.linear_model import LinearRegression

from sibyl.core import Sibyl
from sibyl.db import schema

test_database_name = "sibylapp_test"
test_host = "localhost"
test_port = 27017


@pytest.fixture(scope="session")
def client():
    config = {
        "mongodb": {
            "db": test_database_name,
            "host": test_host,
            "port": test_port,
            "username": None,
            "password": None,
        },
        "log_filename": "test.csv",
        "feature_distribution_location": None,
        "flask": {},
    }
    explorer = Sibyl(config, docker=False)
    app = explorer._init_flask_app("test")
    return app.test_client()


@pytest.fixture(scope="session")
def categories():
    categories = [
        {"name": "cat1", "color": "#000000", "abbreviation": "c1"},
        {"name": "cat2", "abbreviation": "c2"},
    ]
    return categories


@pytest.fixture(scope="session")
def contexts():
    context_1 = {
        "context_id": "context_1",
        "config": {
            "terms": {"A": "a", "B": "b"},
            "A": "abc",
            "B": {"ab": "cd", "ef": "gh"},
        },
    }
    context_2 = {
        "context_id": "context_2",
        "config": {
            "terms": {"C": "c", "D": "d"},
            "A": "def",
            "B": {"12": "34", "56": "78"},
        },
    }
    return [context_1, context_2]


@pytest.fixture(scope="session")
def features():
    features = [
        {
            "name": "num_feat",
            "description": "xyz",
            "negated_description": "not xyz",
            "category": "cat1",
            "type": "numeric",
        },
        {
            "name": "cat_feat",
            "description": "jki",
            "category": "cat2",
            "type": "categorical",
            "values": ["value1", "value2", "value3"],
            "negated_description": "not jki",
        },
        {
            "name": "bin_feat",
            "description": "abc",
            "category": "cat2",
            "type": "boolean",
        },
        {
            "name": "A",
            "description": "feature A",
            "category": "cat2",
            "type": "numeric",
        },
        {
            "name": "B",
            "description": "feature B",
            "category": "cat2",
            "type": "numeric",
        },
        {
            "name": "C",
            "description": "feature C",
            "category": "cat2",
            "type": "numeric",
        },
    ]
    return features


@pytest.fixture(scope="session")
def entities():
    features1 = {
        "A": 14,
        "B": 5,
        "C": 4,
        "num_feat": 10,
        "cat_feat": "value1",
        "bin_feat": True,
    }
    features1_b = {
        "A": 14,
        "B": 5,
        "C": 3,
        "num_feat": 10,
        "cat_feat": "value1",
        "bin_feat": True,
    }
    features2 = {
        "A": 10,
        "B": 1,
        "C": 2,
        "num_feat": 10,
        "cat_feat": "value2",
        "bin_feat": False,
    }
    features2_b = {
        "A": 10,
        "B": 1,
        "C": 1,
        "num_feat": 10,
        "cat_feat": "value2",
        "bin_feat": False,
    }
    features3 = {
        "A": 3,
        "B": -5,
        "C": 4,
        "num_feat": 5,
        "cat_feat": "something",
        "bin_feat": False,
    }

    entities = [
        {
            "eid": "ent1",
            "primary_keys": ["row_a", "row_b"],
            "property": {"group_ids": ["101", "102"]},
        },
        {
            "eid": "ent2",
            "primary_keys": ["row_a", "row_b"],
            "property": {"group_ids": ["101"]},
        },
        {
            "eid": "ent3",
            "primary_keys": ["row_a"],
            "property": {"name": "First Last"},
        },
        {
            "eid": "ent4",
            "primary_keys": ["row_a"],
            "property": {"name": "First Last"},
        },
        {
            "eid": "ent5",
            "primary_keys": ["row_a"],
        },
    ]

    entity_rows = {
        "ent1": [
            {
                "primary_key": "row_a",
                "features": features1,
                "label": "0",
            },
            {
                "primary_key": "row_b",
                "features": features3,
                "label": "1",
            },
        ],
        "ent2": [
            {
                "primary_key": "row_a",
                "features": features1_b,
                "label": "2",
            },
            {
                "primary_key": "row_b",
                "features": features2_b,
                "label": "2",
            },
        ],
        "ent3": [{
            "primary_key": "row_a",
            "features": features2,
            "label": "3",
        }],
        "ent4": [{
            "primary_key": "row_a",
            "features": features2_b,
        }],
        "ent5": [{
            "primary_key": "row_a",
            "features": features3,
        }],
    }

    return entities, entity_rows


@pytest.fixture(scope="session")
def multirow_entities(entities):
    return entities[0:2]


@pytest.fixture(scope="session")
def groups():
    groups = [{"group_id": "101", "property": {"date": "today"}}, {"group_id": "102"}]
    return groups


@pytest.fixture(scope="session")
def models():
    dummy_x = np.zeros((1, 3))
    dummy_y = np.zeros(1)
    model = LinearRegression()
    model.fit(dummy_x, dummy_y)
    model.coef_ = np.array([1, -1, 0])
    model.intercept_ = 0
    columns = ["A", "B", "C", "num_feat", "cat_feat", "bin_feat"]
    dataset = pd.DataFrame(np.random.randint(0, 5, size=(100, 6)), columns=columns)
    transformer = FeatureSelectTransformer(columns=["A", "B", "C"]).fit(dataset)

    realapp = RealApp(model, dataset, transformers=transformer, id_column="eid")
    realapp_serial = pickle.dumps(realapp)

    models = [
        {
            "model_id": "test model",
            "description": "a model",
            "performance": "does well",
            "importances": {"A": 100, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0},
            "realapp": realapp_serial,
        },
        {"model_id": "filler", "realapp": realapp_serial},
    ]
    return models


@pytest.fixture(autouse=True)
def testdb(categories, features, entities, groups, models, contexts):
    client = MongoClient(test_host, test_port)
    client.drop_database(test_database_name)
    connect(test_database_name, host=test_host, port=test_port)

    schema.Category.insert_many(categories)

    schema.Feature.insert_many(features)

    entities, entity_rows = entities
    for item in entities:
        rows = []
        for row in entity_rows[item["eid"]]:
            rows.append(schema.EntityRow.insert(**row))
        item["data"] = rows
        schema.Entity.insert_many([item])

    schema.EntityGroup.insert_many(groups)

    dataset = schema.TrainingSet.insert(
        entities=schema.Entity.find(eid__in=["ent1", "ent2", "ent3"])
    )
    for model in models:
        model["training_set"] = dataset
        schema.Model.insert(**model)

    for context in contexts:
        schema.Context.insert(**context)

    yield client

    client.drop_database(test_database_name)
    disconnect()
