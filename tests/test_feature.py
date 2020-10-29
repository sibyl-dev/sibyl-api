#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sibylapp` package."""


def test_get_categories(client, categories):
    response = client.get('/api/v1/categories/').json

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
    response = client.get('/api/v1/features/').json

    for expected_item in features:
        found = False
        for response_item in response["features"]:
            if response_item["name"] == expected_item["name"]:
                found = True
                for key in ["description", "category", "type"]:
                    if key in expected_item:
                        assert response_item[key] == expected_item[key]
                    else:
                        assert response_item[key] is None
        assert found


def test_get_feature(client, features):
    feature = features[0]
    response = client.get('/api/v1/features/' + feature['name'] + "/").json
    assert response['name'] == feature['name']
    assert response['description'] == feature['description']
    assert response['negated_description'] == feature['negated_description']
    assert response['category'] == feature['category']
    assert response['type'] == response['type']
