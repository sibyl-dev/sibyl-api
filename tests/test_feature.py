#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sibylapp` package."""
import json

from sibyl.db import schema


def test_get_categories(client, categories):
    response = client.get("/api/v1/categories/").json

    for expected_item in categories:
        found = False
        for response_item in response["categories"]:
            if response_item["name"] == expected_item["name"]:
                found = True
                for key in ["color", "abbreviation"]:
                    if key in expected_item:
                        assert response_item[key] == expected_item[key]
                    else:
                        assert response_item[key] is None
        assert found


def test_get_features(client, features):
    response = client.get("/api/v1/features/").json

    for expected_item in features:
        found = False
        for response_item in response["features"]:
            if response_item["name"] == expected_item["name"]:
                found = True
                for key in ["description", "category", "type", "values"]:
                    if key in expected_item:
                        assert response_item[key] == expected_item[key]
                    else:
                        if key == "values":
                            assert response_item[key] == []
                        else:
                            assert response_item[key] is None
        assert found


def test_get_feature(client, features):
    feature = features[0]
    response = client.get("/api/v1/features/" + feature["name"] + "/").json
    assert response["name"] == feature["name"]
    assert response["description"] == feature["description"]
    assert response["negated_description"] == feature["negated_description"]
    assert response["category"] == feature["category"]
    assert response["type"] == response["type"]
    assert response["values"] == []

    feature = features[1]
    response = client.get("/api/v1/features/" + feature["name"] + "/").json
    assert response["values"] == feature["values"]


def test_update_existing_feature_with_valid_data(client, features):
    feature_name = features[0]["name"]
    feature_data = {
        "description": "Updated description",
        "type": "numeric",
        "category": "cat1",
    }

    response = client.put("/api/v1/features/" + feature_name + "/", json=feature_data).json
    assert response["name"] == feature_name
    for key in feature_data:
        assert response[key] == feature_data[key]

    # Confirm that feature got update in the database
    updated_feature = schema.Feature.find_one(name=feature_name)
    assert updated_feature is not None
    for key in features[0]:
        if key in feature_data:
            assert updated_feature[key] == feature_data[key]
        else:
            assert updated_feature[key] == features[0][key]


def test_add_feature_with_valid_data(client, features):
    feature_name = "new_feature"
    feature_data = {
        "description": "Updated description",
        "type": "numeric",
        "category": "new_category",
    }

    response = client.put("/api/v1/features/" + feature_name + "/", json=feature_data).json
    assert response["name"] == feature_name
    for key in feature_data:
        assert response[key] == feature_data[key]

    # Confirm that feature got update in the database
    updated_feature = schema.Feature.find_one(name=feature_name)
    assert updated_feature is not None
    for key in features[1]:  # Just to get all keys
        if key in feature_data:
            assert updated_feature[key] == feature_data[key]
        elif key != "name":
            assert not updated_feature[key]

    # assert new category was created
    assert schema.Category.find_one(name="new_category") is not None


def test_add_or_modify_multiple(client, features):
    feature_data = [
        {
            "name": features[0]["name"],
            "description": "Updated description",
            "type": "numeric",
            "category": "cat1",
        },
        {
            "name": "new_feature",
            "description": "Updated description",
            "type": "numeric",
            "category": "new_category",
        },
    ]

    response = client.put("/api/v1/features/", json={"features": feature_data}).json
    assert len(response) == len(feature_data)
    for i in range(len(feature_data)):
        for key in feature_data[i]:
            assert response[i][key] == feature_data[i][key]

    for i in range(len(feature_data)):
        updated_feature = schema.Feature.find_one(name=feature_data[i]["name"])
        assert updated_feature is not None
        for key in features[0]:
            if key in feature_data[i]:
                assert updated_feature[key] == feature_data[i][key]
            elif key != "name":
                if i == 0:  # Existing feature
                    assert updated_feature[key] == features[0][key]
                else:  # New feature
                    assert not updated_feature[key]
