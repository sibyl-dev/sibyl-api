import pytest
from sibylapp.core import SibylApp
from mongoengine import connect
from mongoengine.connection import disconnect
from sibylapp.db import schema
from pymongo import MongoClient

test_database_name = 'sibylapp_test'
test_host = "localhost"
test_port = 27017


@pytest.fixture(scope="module")
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


@pytest.fixture(scope="module")
def categories():
    categories = [{"name": "cat1", "color": "#000000", "abbreviation": "c1"},
                  {"name": "cat2", "abbreviation": "c2"}]
    return categories


@pytest.fixture(scope="module")
def features():
    features = [{"name": "feat1", "description": "xyz", "category": "cat1", "type": "numeric"},
                {"name": "feat2", "description": "jki", "category": "cat2", "type": "categorical"}]
    return features


@pytest.fixture(scope="module", autouse=True)
def testdb(categories, features):
    print("making database")
    client = MongoClient("localhost", 27017)
    connect(test_database_name, host=test_host, port=test_port)

    schema.Category.insert_many(categories)

    for item in features:
        item_with_ref = item.copy()
        reference = schema.Category.find_one(name=item["category"])
        item_with_ref["category"] = reference
        schema.Feature.insert(**item_with_ref)

    yield

    client.drop_database(test_database_name)
    disconnect()
