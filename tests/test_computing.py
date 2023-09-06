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
    for eid in [entity["eid"] for entity in entities]:  # Assert no error
        pd.read_json(contributions[eid], orient="index")

    response = client.post(
        "/api/v1/multi_contributions/",
        json={"eids": [entities[0]["eid"]], "model_id": model_id},
    ).json
    contributions = response["contributions"]
    for row_id in entities[0]["row_ids"]:  # Assert no error
        pd.read_json(contributions[row_id], orient="index")


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

    changes = {"A": 6, "C": 5}
    response = client.post(
        "/api/v1/modified_prediction/",
        json={"eid": eid, "model_id": model_id, "changes": changes, "row_id": "row_b"},
    ).json
    assert response["prediction"] == (6 - entity["features"]["row_b"]["B"])


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

    changes = {"A": 5}
    response = client.post(
        "/api/v1/single_change_predictions/",
        json={"eid": eid, "model_id": model_id, "changes": changes, "row_id": "row_b"},
    ).json
    assert response["predictions"] == [["A", 5 - entity["features"]["row_b"]["B"]]]


def test_modified_contribution(client, models, entities):
    def helper(resp, row_id):
        contribution = resp["contribution"]
        df = pd.read_json(contribution, orient="index")

        assert len(df.index) == len(entity["features"][row_id])
        assert "Feature Value" in df.columns
        assert "Contribution" in df.columns
        assert "Average/Mode" in df.columns

    model_id = str(schema.Model.find_one(name=models[0]["name"]).id)
    entity = entities[0]
    eid = entity["eid"]

    changes = {"A": 5}
    response = client.post(
        "/api/v1/modified_contribution/",
        json={"eid": eid, "model_id": model_id, "changes": changes},
    ).json
    helper(response, "row_a")

    changes = {"A": 3, "B": 12, "C": 1}
    response = client.post(
        "/api/v1/modified_contribution/",
        json={"eid": eid, "model_id": model_id, "changes": changes},
    ).json
    helper(response, "row_a")

    changes = {"A": 3, "B": 12, "C": 1}
    response = client.post(
        "/api/v1/modified_contribution/",
        json={"eid": eid, "model_id": model_id, "changes": changes, "row_id": "row_b"},
    ).json
    helper(response, "row_b")


def test_post_similar_entities(client, models, entities):
    model_id = str(schema.Model.find_one(name=models[0]["name"]).id)
    response = client.post(
        "/api/v1/similar_entities/",
        json={"eids": [entity["eid"] for entity in entities], "model_id": model_id},
    ).json
    similar_entities = response["similar_entities"]

    for eid in [entity["eid"] for entity in entities]:  # Assert no error
        pd.read_json(similar_entities[eid]["X"], orient="index")
        pd.read_json(similar_entities[eid]["y"], orient="index")

    response = client.post(
        "/api/v1/similar_entities/",
        json={
            "eids": [entities[0]["eid"]],
            "model_id": model_id,
        },
    ).json
    similar_entities = response["similar_entities"]
    for row_id in entities[0]["row_ids"]:  # Assert no error
        pd.read_json(similar_entities[row_id]["X"], orient="index")
        pd.read_json(similar_entities[row_id]["y"], orient="index")
