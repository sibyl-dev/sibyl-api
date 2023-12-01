#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sibylapp` package."""

from sibyl.db import schema


def test_get_models(client, models):
    response = client.get("/api/v1/models/").json
    assert len(response["models"]) == len(models)
    for expected_item in models:
        found = False
        for response_item in response["models"]:
            schema.Model.find_one(model_id=response_item["model_id"])  # assert no error
            # assert model in models
            if response_item["model_id"] == expected_item["model_id"]:
                found = True
        assert found


def test_get_model(client, models):
    model_id = str(schema.Model.find_one(model_id=models[0]["model_id"]).model_id)
    response = client.get("/api/v1/models/" + model_id + "/").json
    assert len(response) == 3
    assert response["model_id"] == model_id
    for key in ["model_id", "description", "performance"]:
        assert response[key] == models[0][key]


def test_get_importance(client, models):
    model_id = str(schema.Model.find_one(model_id=models[0]["model_id"]).model_id)
    response = client.get("/api/v1/importance/?model_id=" + model_id).json

    assert response["importances"] == models[0]["importances"]


def test_get_prediction(client, models, entities):
    model_id = str(schema.Model.find_one(model_id=models[0]["model_id"]).model_id)
    entity = entities[1]
    expected_output = entity["features"]["row_a"]["A"] - entity["features"]["row_a"]["B"]

    response = client.get(
        "/api/v1/prediction/?model_id=" + model_id + "&eid=" + entity["eid"]
    ).json
    assert response["output"] == expected_output

    entity = entities[0]
    row_id = "row_b"
    expected_output = entity["features"][row_id]["A"] - entity["features"][row_id]["B"]

    response = client.get(
        "/api/v1/prediction/?model_id=" + model_id + "&eid=" + entity["eid"] + "&row_id=" + row_id
    ).json
    assert response["output"] == expected_output


def test_multi_prediction(client, models, entities, multirow_entities):
    model_id = str(schema.Model.find_one(model_id=models[0]["model_id"]).model_id)

    response = client.post(
        "/api/v1/multi_prediction/",
        json={"eids": [entity["eid"] for entity in entities], "model_id": model_id},
    ).json

    for entity in entities:
        features = next(iter(entity["features"].values()))
        assert response["predictions"][entity["eid"]] == features["A"] - features["B"]

    response = client.post(
        "/api/v1/multi_prediction/",
        json={
            "eids": [entity["eid"] for entity in multirow_entities],
            "model_id": model_id,
            "row_ids": ["row_b"],
        },
    ).json

    for entity in multirow_entities:
        features = entity["features"]["row_b"]
        assert response["predictions"][entity["eid"]] == features["A"] - features["B"]


def test_multi_prediction_multi_rows(client, models, multirow_entities):
    model_id = str(schema.Model.find_one(model_id=models[0]["model_id"]).model_id)
    entity = multirow_entities[0]

    response = client.post(
        "/api/v1/multi_prediction/",
        json={
            "eids": [entity["eid"]],
            "model_id": model_id,
            "row_ids": entity["row_ids"],
        },
    ).json

    for row in entity["row_ids"]:
        features = entity["features"][row]
        assert response["predictions"][row] == features["A"] - features["B"]
