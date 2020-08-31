#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sibylapp` package."""

from sibylapp.db import schema


def test_post_contributions(client, models, entities):
    entity = entities[0]
    model_id = str(schema.Model.find_one(name=models[0]["name"]).id)
    response = client.post('/api/v1/contributions/',
                           json={"eid": entity["eid"], "model_id": model_id}).json
    contributions = response["contributions"]
    assert len(contributions) == 3
    assert "A" in contributions
    assert abs(contributions["A"]) > .0001

    assert "B" in contributions
    assert abs(contributions["B"]) < .00001

    assert "C" in contributions
    assert abs(contributions["C"]) < .00001


def test_post_feature_distributions(client, models):
    model_id = str(schema.Model.find_one(name=models[0]["name"]).id)
    prediction = 10

    response = client.post('/api/v1/feature_distributions/',
                           json={"prediction": prediction, "model_id": model_id}).json

    expected_distributions = {"A": {"type": "numeric", "metrics": [10, 10, 10, 10, 10]},
                              "B": {"type": "numeric", "metrics": [1, 1, 3, 5, 5]},
                              "C": {"type": "numeric", "metrics": [4, 4, 4, 4, 4]},
                              "num_feat": {"type": "numeric", "metrics": [10, 10, 10, 10, 10]},
                              "cat_feat": {"type": "categorical", "metrics":
                                  [["value1", "value2"], [2, 2]]},
                              "bin_feat": {"type": "categorical", "metrics":
                                  [[False, True], [2, 2]]}}
    assert response["distributions"] == expected_distributions


def test_post_prediction_count(client, models):
    model_id = str(schema.Model.find_one(name=models[0]["name"]).id)
    prediction = 10

    response = client.post('/api/v1/prediction_count/',
                           json={"prediction": prediction, "model_id": model_id}).json

    assert response["count"] == 4


