#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sibylapp` package."""

import pandas as pd

from sibyl.db import schema


def contribution_helper(contributions, b_neg):
    assert len(contributions) == 6
    assert "A" in contributions
    assert contributions["A"] > 0.01

    assert "B" in contributions
    if b_neg:
        assert contributions["B"] < -0.01
    else:
        assert contributions["B"] > 0.01

    assert "C" in contributions
    assert abs(contributions["C"]) < 0.0001

    for col in ["num_feat", "cat_feat", "bin_feat"]:
        assert col in contributions
        assert abs(contributions[col]) < 0.0001


def test_post_contributions(client, models, entities):
    entity = entities[0]
    model_id = str(schema.Model.find_one(name=models[0]["name"]).id)

    response = client.post(
        "/api/v1/contributions/", json={"eid": entity["eid"], "model_id": model_id}
    ).json
    contributions = response["contributions"]
    contribution_helper(contributions, True)

    row_id = "row_b"
    response = client.post(
        "/api/v1/contributions/",
        json={"eid": entity["eid"], "model_id": model_id, "row_id": row_id},
    ).json
    contributions = response["contributions"]
    contribution_helper(contributions, False)


def test_post_multi_contributions(client, models, entities, multirow_entities):
    model_id = str(schema.Model.find_one(name=models[0]["name"]).id)
    response = client.post(
        "/api/v1/multi_contributions/",
        json={"eids": [entity["eid"] for entity in entities], "model_id": model_id},
    ).json
    contributions = response["contributions"]
    assert len(contributions) == len(entities)
    for eid in [entity["eid"] for entity in entities]:  # Assert no error
        pd.DataFrame.from_dict(contributions[eid], orient="index")
    conts_0 = contributions[entities[0]["eid"]]
    assert conts_0.keys() == next(iter(entities[0]["features"].values())).keys()
    assert conts_0["A"]["Contribution"] > 0.01
    assert conts_0["B"]["Contribution"] < -0.01

    response = client.post(
        "/api/v1/multi_contributions/",
        json={
            "eids": [entity["eid"] for entity in multirow_entities],
            "model_id": model_id,
            "row_id": "row_b",
        },
    ).json
    contributions = response["contributions"]
    for eid in [entity["eid"] for entity in multirow_entities]:  # Assert no error
        pd.DataFrame.from_dict(contributions[eid], orient="index")
    conts_0 = contributions[multirow_entities[0]["eid"]]
    assert conts_0.keys() == next(iter(multirow_entities[0]["features"].values())).keys()
    assert conts_0["A"]["Contribution"] > 0.01
    assert conts_0["B"]["Contribution"] > 0.01


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


def test_post_similar_entities(client, models, entities, multirow_entities):
    model_id = str(schema.Model.find_one(name=models[0]["name"]).id)
    response = client.post(
        "/api/v1/similar_entities/",
        json={"eids": [entity["eid"] for entity in entities], "model_id": model_id},
    ).json
    similar_entities = response["similar_entities"]

    for i, eid in enumerate([entity["eid"] for entity in entities]):
        assert next(iter(similar_entities[eid]["X"].values())) == entities[i]["features"]["row_a"]
        pd.DataFrame.from_dict(similar_entities[eid]["X"], orient="index")  # Assert no error
        pd.Series(similar_entities[eid]["y"])  # Assert no error
        pd.Series(similar_entities[eid]["Input"])  # Assert no error

    response = client.post(
        "/api/v1/similar_entities/",
        json={
            "eids": [entity["eid"] for entity in multirow_entities],
            "model_id": model_id,
            "row_id": "row_b",
        },
    ).json
    similar_entities = response["similar_entities"]
    for i, eid in enumerate([entity["eid"] for entity in multirow_entities]):
        assert next(iter(similar_entities[eid]["X"].values())) == entities[i]["features"]["row_b"]
        pd.DataFrame.from_dict(similar_entities[eid]["X"], orient="index")  # Assert no error
        pd.Series(similar_entities[eid]["y"])  # Assert no error
        pd.Series(similar_entities[eid]["Input"])  # Assert no error
