#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sibylapp` package."""
from sibyl.db import schema


def test_get_entities(client, entities):
    response = client.get("/api/v1/entities/").json

    assert len(response["entities"]) == len(entities)

    for expected_item in entities:
        found = False
        for response_item in response["entities"]:
            if response_item["eid"] == expected_item["eid"]:
                found = True
                if "property" in expected_item:
                    assert response_item["property"] == expected_item["property"]
                else:
                    assert len(response_item["property"]) == 0
                if "row_ids" in expected_item:
                    assert response_item["row_ids"] == expected_item["row_ids"]
        assert found


def test_get_entity(client, entities):
    entity = entities[0]
    response = client.get("/api/v1/entities/" + entity["eid"] + "/").json
    assert response["eid"] == entity["eid"]
    assert response["features"] == entity["features"]
    assert response["property"] == entity["property"]
    # We may remove row_ids from the response as they can be found in features, but if they are
    #   there they should be correct
    if "row_ids" in response:
        assert response["row_ids"] == entity["row_ids"]


def test_get_entity_with_row(client, entities):
    entity = entities[0]
    row_id = entity["row_ids"][1]
    response = client.get("/api/v1/entities/" + entity["eid"] + "/?row_id=" + row_id).json

    assert response["eid"] == entity["eid"]
    assert response["features"] == entity["features"][row_id]
    assert response["property"] == entity["property"]


def test_get_groups(client, groups):
    response = client.get("/api/v1/groups/").json
    assert response["groups"] == [group["group_id"] for group in groups]


def test_get_group(client, groups):
    group = groups[0]
    response = client.get("/api/v1/groups/" + group["group_id"] + "/").json
    assert response == group


def test_entities_in_group(client):
    group_id = "101"
    entities_involved = ["ent1", "ent2"]
    response = client.get("/api/v1/entities/?group_id=" + group_id).json
    assert response == entities_involved


def test_update_existing_entity_with_valid_data(client, entities):
    eid = entities[0]["eid"]
    entity_data = {
        "features": {"row_a": {"A": 1, "B": 2}},
    }

    response = client.put("/api/v1/entities/" + eid + "/", json=entity_data).json
    assert response["eid"] == eid
    for key in entity_data:
        assert response[key] == entity_data[key]

    # Confirm that feature got update in the database
    updated_entity = schema.Entity.find_one(eid=eid)
    assert updated_entity is not None
    for key in entities[0]:
        if key in entity_data:
            assert updated_entity[key] == entity_data[key]
        elif key != "events":  # ignore events for now
            assert updated_entity[key] == entities[0][key]


def test_add_entity_with_valid_data(client, entities):
    eid = "new_entity"
    entity_data = {
        "features": {"row_a": {"A": 1, "B": 2}},
    }

    response = client.put("/api/v1/entities/" + eid + "/", json=entity_data).json
    assert response["eid"] == eid
    for key in entity_data:
        assert response[key] == entity_data[key]

    # Confirm that feature got update in the database
    updated_entity = schema.Entity.find_one(eid=eid)
    assert updated_entity is not None
    for key in entities[0]:
        if key in entity_data:
            assert updated_entity[key] == entity_data[key]
        elif key == "row_ids":
            assert updated_entity[key] == ["row_a"]
        elif key != "eid":
            assert not updated_entity[key]


def test_add_or_modify_multiple(client, entities):
    entity_data = [
        {
            "eid": entities[0]["eid"],
            "labels": {"row_a": 1, "row_b": 2},
        },
        {
            "eid": "new_feature",
            "features": {"row_a": {"A": 1, "B": 2}},
            "labels": {"row_a": 1, "row_b": 2},
        },
    ]

    response = client.put("/api/v1/entities/", json={"entities": entity_data}).json
    assert len(response) == len(entity_data)
    for i in range(len(entity_data)):
        for key in entity_data[i]:
            assert response[i][key] == entity_data[i][key]

    for i in range(len(entity_data)):
        updated_entity = schema.Entity.find_one(eid=entity_data[i]["eid"])
        assert updated_entity is not None
        for key in entities[0]:
            if key in entity_data[i]:
                assert updated_entity[key] == entity_data[i][key]
            elif key != "eid" and key != "events":
                if i == 0:  # Existing entity
                    assert updated_entity[key] == entities[0][key]
                else:  # New entity
                    if key == "row_ids":
                        assert updated_entity[key] == ["row_a"]
                    else:
                        assert not updated_entity[key]
