#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sibylapp` package."""


def test_categories(client, categories):
    response = client.get('/api/v1/categories/').json

    expected_items = {}
    for item in categories:
        name = item.pop('name')
        expected_items[name] = item
    for item in response["categories"]:
        assert item['name'] in expected_items
        for key in ["color", "abbreviation"]:
            if key in expected_items[item['name']]:
                assert item[key] == expected_items[item['name']][key]
            else:
                assert item[key] is None


def test_feature(client, features):
    response = client.get('/api/v1/features/').json
    expected_items = {}
    for item in features:
        name = item.pop('name')
        expected_items[name] = item
    for item in response["features"]:
        assert item['name'] in expected_items
        for key in ["description", "category", "type"]:
            if key in expected_items[item['name']]:
                assert item[key] == expected_items[item['name']][key]
            else:
                assert item[key] is None


