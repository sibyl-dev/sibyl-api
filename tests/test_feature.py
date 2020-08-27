#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sibylapp` package."""


def test_categories(client, categories):
    response = client.get('/api/v1/categories/').json

    expected_categories = {}
    for item in categories:
        name = item.pop('name')
        expected_categories[name] = item
    for cat in response["categories"]:
        assert cat['name'] in expected_categories
        if 'color' in expected_categories[cat['name']]:
            assert cat['color'] == expected_categories[cat['name']]['color']
        else:
            assert cat['color'] is None


def test_feature(client, features):
    response = client.get('/api/v1/features/').json


