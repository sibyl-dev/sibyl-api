import datetime
import pickle

import numpy as np
import pandas as pd
import pytest
from mongoengine import connect
from mongoengine.connection import disconnect
from pymongo import MongoClient
from pyreal.explainers import LocalFeatureContribution
from sklearn.linear_model import LinearRegression

from sibylapp.core import SibylApp
from sibylapp.db import schema

test_database_name = 'sibylapp_test'
test_host = "localhost"
test_port = 27017


@pytest.fixture(scope="session")
def app():
    config = {"db": test_database_name,
              "host": test_host,
              "port": test_port,
              "username": None,
              "password": None,
              "log_filename": "test.csv",
              "feature_distribution_location": None}
    explorer = SibylApp(config, docker=False)
    app = explorer._init_flask_app('test')
    return app


@pytest.fixture(scope="session")
def categories():
    categories = [{"name": "cat1", "color": "#000000", "abbreviation": "c1"},
                  {"name": "cat2", "abbreviation": "c2"}]
    return categories


@pytest.fixture(scope="session")
def features():
    features = [{"name": "num_feat", "description": "xyz", "negated_description": "not xyz",
                 "category": "cat1", "type": "numeric"},
                {"name": "cat_feat", "description": "jki",
                 "category": "cat2", "type": "categorical"},
                {"name": "bin_feat", "description": "abc",
                 "category": "cat2", "type": "binary"},
                {"name": "A", "description": "feature A",
                 "category": "cat2", "type": "numeric"},
                {"name": "B", "description": "feature B",
                 "category": "cat2", "type": "numeric"},
                {"name": "C", "description": "feature C",
                 "category": "cat2", "type": "numeric"}
                ]
    return features


@pytest.fixture(scope="session")
def entities():
    events = [
        {"event_id": "123", "datetime": datetime.datetime(2020, 1, 1),
         "type": "type1", "property": {"prop1": "x"}},
        {"event_id": "456", "datetime": datetime.datetime(2020, 5, 1),
         "type": "type2", "property": {"prop1": "y"}},
        {"event_id": "789", "datetime": datetime.datetime(2019, 6, 15),
         "type": "type1", "property": {"prop1": "x"}},
    ]

    features1 = {"A": 14, "B": 5, "C": 4, "num_feat": 10, "cat_feat": "value1", "bin_feat": True}
    features1_b = {"A": 14, "B": 5, "C": 3, "num_feat": 10, "cat_feat": "value1", "bin_feat": True}
    features2 = {"A": 10, "B": 1, "C": 2, "num_feat": 10, "cat_feat": "value2", "bin_feat": False}
    features2_b = {"A": 10, "B": 1, "C": 1, "num_feat": 10, "cat_feat": "value2",
                   "bin_feat": False}
    features3 = {"A": 2, "B": 5, "C": 4, "num_feat": 5, "cat_feat": "something", "bin_feat": False}

    entities = [{"eid": "ent1", "property": {"referral_ids": ["101", "102"]},
                 "features": features1, "events": [events[0], events[1]]},
                {"eid": "ent2", "property": {"referral_ids": ["101"]}, "features": features1_b},
                {"eid": "ent3", "property": {"name": "First Last"}, "features": features2},
                {"eid": "ent4", "property": {"name": "First Last"}, "features": features2_b},
                {"eid": "ent5", "features": features3, "events": [events[2]]}]
    return entities


@pytest.fixture(scope="session")
def referrals():
    referrals = [{"referral_id": "101", "property": {"date": "today"}}, {"referral_id": "102"}]
    return referrals


class TestTransformer:
    def fit(self):
        return self

    def transform(self, x):
        return x[["A", "B", "C"]]

    def transform_contributions(self, contributions):
        return contributions[["A", "B", "C"]]


@pytest.fixture(scope="session")
def models():
    dummy_x = np.zeros((1, 3))
    dummy_y = np.zeros(1)
    model = LinearRegression()
    model.fit(dummy_x, dummy_y)
    model.coef_ = np.array([1, -1, 0])
    model.intercept_ = 0
    model_serial = pickle.dumps(model)
    transformer = TestTransformer()
    transformer_serial = pickle.dumps(transformer)

    dataset = pd.DataFrame(np.random.randint(0, 5, size=(100, 6)), columns=list("ABCDEF"))

    # TODO: Replace with LocalFeatureContribution once LocalFeatureContribution supports
    #       kernel keyword
    explainer = LocalFeatureContribution(model, dataset, e_transforms=transformer,
                                         contribution_transforms=transformer,
                                         e_algorithm="shap", fit_on_init=True)
    explainer_serial = pickle.dumps(explainer)

    models = [{"model": model_serial, "transformer": transformer_serial,
               "name": "test model", "description": "a model", "performance": "does well",
               "importances": {"A": 100, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0},
               "explainer": explainer_serial},
              {"model": model_serial, "name": "filler"}]
    return models


@pytest.fixture(scope="session", autouse=True)
def testdb(categories, features, entities, referrals, models):
    client = MongoClient("localhost", 27017)
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

    schema.Referral.insert_many(referrals)

    dataset = schema.TrainingSet.insert(entities=schema.Entity.find())
    for model in models:
        model["training_set"] = dataset
        schema.Model.insert(**model)

    yield

    client.drop_database(test_database_name)
    disconnect()
