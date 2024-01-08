#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sibylapp` package."""

from sibyl.db import schema


def test_get_contexts(client, contexts):
    response = client.get("/api/v1/contexts/").json
    assert len(response["contexts"]) == len(contexts)
    for expected_item in contexts:
        found = False
        for response_item in response["contexts"]:
            found_context = schema.Context.find_one(context_id=response_item["context_id"])
            if found_context["config"] == expected_item["config"]:
                found = True
        assert found


def test_get_context(client, contexts):
    for context in contexts:
        context_response = client.get("/api/v1/context/" + context["context_id"] + "/").json[
            "context"
        ]
        print(context_response)
        assert context_response in contexts


def test_modify_context(client, contexts):
    context_id = contexts[0]["context_id"]
    changes = {"new": "config"}
    context_response = client.put("/api/v1/context/" + context_id + "/", json=changes).json[
        "context"
    ]["config"]

    context = schema.Context.find_one(context_id=context_id)["config"]
    for key in context:
        if key in changes:
            assert context[key] == changes[key]
            assert context_response[key] == changes[key]
        else:
            assert context[key] == contexts[0]["config"][key]
            assert context_response[key] == contexts[0]["config"][key]


def test_add_context(client, contexts):
    context_id = "new_context"
    new_config = {"new": "config", "terms": {"A": "a", "B": "b"}}
    context_response = client.put("/api/v1/context/" + context_id + "/", json=new_config).json[
        "context"
    ]["config"]

    context = schema.Context.find_one(context_id=context_id)["config"]

    for key in context:
        assert key in new_config
        assert context[key] == new_config[key]
        assert context_response[key] == new_config[key]
