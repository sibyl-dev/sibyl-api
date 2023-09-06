#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sibylapp` package."""

import pandas as pd

from sibyl.db import schema


def test_post_contributions(client, models, entities):
    def helper(conts, b_neg):
        assert len(conts) == 6
        assert "A" in conts
        assert conts["A"] > 0.01

        assert "B" in conts
        if b_neg:
            assert conts["B"] < -0.01
        else:
            assert conts["B"] > 0.01

        assert "C" in conts
        assert abs(conts["C"]) < 0.0001

        for col in ["num_feat", "cat_feat", "bin_feat"]:
            assert col in conts
            assert abs(conts[col]) < 0.0001

    entity = entities[0]
    model_id = str(schema.Model.find_one(name=models[0]["name"]).id)

    response = client.post(
        "/api/v1/contributions/", json={"eid": entity["eid"], "model_id": model_id}
    ).json
    contributions = response["contributions"]
    helper(contributions, True)

    row_id = "row_b"
    response = client.post(
        "/api/v1/contributions/",
        json={"eid": entity["eid"], "model_id": model_id, "row_id": row_id},
    ).json
    contributions = response["contributions"]
    helper(contributions, False)


def test_post_multi_contributions(client, models, entities):
    model_id = str(schema.Model.find_one(name=models[0]["name"]).id)
    response = client.post(
        "/api/v1/multi_contributions/",
        json={"eids": [entity["eid"] for entity in entities], "model_id": model_id},
    ).json
    contributions = response["contributions"]
    assert len(contributions) == len(entities)
    for eid in contributions:  # Assert no error
        pd.read_json(contributions[eid], orient="index")


def test_post_modified_prediction(client, models, entities):
    model_id = str(schema.Model.find_one(name=models[0]["name"]).id)
    entity = entities[0]
    eid = entity["eid"]

    changes = {"A": 5}
    response = client.post(
        "/api/v1/modified_prediction/",
        json={"eid": eid, "model_id": model_id, "changes": changes},
    ).json
    assert response["prediction"] == (5 - entity["features"]["row_a"]["B"])

    changes = {"A": 6, "B": 10, "C": 5}
    response = client.post(
        "/api/v1/modified_prediction/",
        json={"eid": eid, "model_id": model_id, "changes": changes},
    ).json
    assert response["prediction"] == -4


def test_single_change_predictions(client, models, entities):
    model_id = str(schema.Model.find_one(name=models[0]["name"]).id)
    entity = entities[0]
    eid = entity["eid"]

    changes = {"A": 5}
    response = client.post(
        "/api/v1/single_change_predictions/",
        json={"eid": eid, "model_id": model_id, "changes": changes},
    ).json
    assert response["predictions"] == [["A", 5 - entity["features"]["row_a"]["B"]]]

    changes = {"A": 6, "B": 10, "C": 5}
    response = client.post(
        "/api/v1/single_change_predictions/",
        json={"eid": eid, "model_id": model_id, "changes": changes},
    ).json
    assert response["predictions"] == [
        ["A", 6 - entity["features"]["row_a"]["B"]],
        ["B", entity["features"]["row_a"]["A"] - 10],
        ["C", entity["features"]["row_a"]["A"] - entity["features"]["row_a"]["B"]],
    ]


def test_modified_contribution(client, models, entities):
    model_id = str(schema.Model.find_one(name=models[0]["name"]).id)
    entity = entities[0]
    eid = entity["eid"]

    changes = {"A": 5}
    response = client.post(
        "/api/v1/modified_contribution/",
        json={"eid": eid, "model_id": model_id, "changes": changes},
    ).json
    contribution = response["contribution"]
    df = pd.read_json(contribution, orient="index")

    assert len(df.index) == len(entity["features"]["row_a"])
    assert "Feature Value" in df.columns
    assert "Contribution" in df.columns
    assert "Average/Mode" in df.columns

    changes = {"A": 3, "B": 12, "C": 1}
    response = client.post(
        "/api/v1/modified_contribution/",
        json={"eid": eid, "model_id": model_id, "changes": changes},
    ).json
    contribution = response["contribution"]
    df = pd.read_json(contribution, orient="index")

    assert len(df.index) == len(entity["features"]["row_a"])
    assert "Feature Value" in df.columns
    assert "Contribution" in df.columns
    assert "Average/Mode" in df.columns


def test_post_similar_entities(client, models, entities):
    model_id = str(schema.Model.find_one(name=models[0]["name"]).id)
    response = client.post(
        "/api/v1/similar_entities/",
        json={"eids": [entity["eid"] for entity in entities], "model_id": model_id},
    ).json
    similar_entities = response["similar_entities"]
    assert len(similar_entities) == len(entities)
    for eid in similar_entities:  # Assert no error
        pd.read_json(similar_entities[eid]["X"], orient="index")
        pd.read_json(similar_entities[eid]["y"], orient="index")
