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
            found_context = schema.Context.find_one(id=response_item["id"])
            if found_context["terms"] == expected_item["terms"]:
                found = True
        assert found


def test_get_context(client, contexts):
    for context in client.get("/api/v1/contexts/").json["contexts"]:
        context_id = context["id"]
        context_response = client.get("/api/v1/context/" + context_id + "/").json["context"]
        del context_response["id"]
        assert context_response in contexts
