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
            model = schema.Model.find_one(id=response_item["id"])  # assert no error
            # assert model in models
            if response_item["name"] == expected_item["name"]:
                found = True
        assert found


def test_get_model(client, models):
    model_id = str(schema.Model.find_one(name=models[0]["name"]).id)
    response = client.get("/api/v1/models/" + model_id + "/").json
    assert len(response) == 4
    assert response["id"] == model_id
    for key in ["name", "description", "performance"]:
        assert response[key] == models[0][key]


def test_get_importance(client, models):
    model_id = str(schema.Model.find_one(name=models[0]["name"]).id)
    response = client.get("/api/v1/importance/?model_id=" + model_id).json

    assert response["importances"] == models[0]["importances"]


def test_get_prediction(client, models, entities):
    model_id = str(schema.Model.find_one(name=models[0]["name"]).id)
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
