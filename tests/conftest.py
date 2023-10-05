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
        "terms": {"A": "a", "B": "b"},
        "gui_preset": "abc",
        "gui_config": {"ab": "cd", "ef": "gh"},
    }
    context_2 = {
        "terms": {"C": "c", "D": "d"},
        "gui_preset": "def",
        "gui_config": {"12": "34", "56": "78"},
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
        },
        {
            "name": "bin_feat",
            "description": "abc",
            "category": "cat2",
            "type": "binary",
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
    events = [
        {
            "event_id": "123",
            "datetime": datetime.datetime(2020, 1, 1),
            "type": "type1",
            "property": {"prop1": "x"},
        },
        {
            "event_id": "456",
            "datetime": datetime.datetime(2020, 5, 1),
            "type": "type2",
            "property": {"prop1": "y"},
        },
        {
            "event_id": "789",
            "datetime": datetime.datetime(2019, 6, 15),
            "type": "type1",
            "property": {"prop1": "x"},
        },
    ]

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
            "row_ids": ["row_a", "row_b"],
            "property": {"group_ids": ["101", "102"]},
            "features": {"row_a": features1, "row_b": features3},
            "labels": {"row_b": 1, "row_a": 0},
            "events": [events[0], events[1]],
        },
        {
            "eid": "ent2",
            "row_ids": ["row_a", "row_b"],
            "property": {"group_ids": ["101"]},
            "features": {"row_a": features1_b, "row_b": features2_b},
            "labels": {"row_a": 2, "row_b": 2},
        },
        {
            "eid": "ent3",
            "row_ids": ["row_a"],
            "property": {"name": "First Last"},
            "features": {"row_a": features2},
            "labels": {"row_a": 3},
        },
        {
            "eid": "ent4",
            "row_ids": ["row_a"],
            "property": {"name": "First Last"},
            "features": {"row_a": features2_b},
        },
        {
            "eid": "ent5",
            "row_ids": ["row_a"],
            "features": {"row_a": features3},
            "events": [events[2]],
        },
    ]
    return entities


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
    model_serial = pickle.dumps(model)
    columns = ["A", "B", "C", "num_feat", "cat_feat", "bin_feat"]
    dataset = pd.DataFrame(np.random.randint(0, 5, size=(100, 6)), columns=columns)
    transformer = FeatureSelectTransformer(columns=["A", "B", "C"]).fit(dataset)

    explainer = RealApp(model, dataset, transformers=transformer, id_column="eid")
    explainer_serial = pickle.dumps(explainer)

    models = [
        {
            "model": model_serial,
            "model_id": "test model",
            "description": "a model",
            "performance": "does well",
            "importances": {"A": 100, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0},
            "explainer": explainer_serial,
        },
        {"model": model_serial, "model_id": "filler", "explainer": explainer_serial},
    ]
    return models


@pytest.fixture(scope="session", autouse=True)
def testdb(categories, features, entities, groups, models, contexts):
    client = MongoClient("localhost", 27017)
    client.drop_database(test_database_name)
    connect(test_database_name, host=test_host, port=test_port)

    schema.Category.insert_many(categories)

    for item in features:
        item_with_ref = item.copy()
        reference = schema.Category.find_one(name=item["category"])
        item_with_ref["category"] = reference
        schema.Feature.insert(**item_with_ref)

    for item in entities:
        item_with_ref = item.copy()
        if "events" in item_with_ref:
            ref_events = []
            for event in item_with_ref["events"]:
                ref = schema.Event.insert(**event)
                ref_events.append(ref)
            item_with_ref["events"] = ref_events
        schema.Entity.insert_many([item_with_ref])  # this line does not appear to work with insert

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
