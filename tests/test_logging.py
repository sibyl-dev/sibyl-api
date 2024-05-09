import datetime

from sibyl.db import schema


def test_post_logging_all_inputs(client):
    event = {
        "element": "something",
        "action": "click",
        "details": {"detail": "A"},
        "interface": "interface_1",
    }
    timestamp = 1000
    user_id = "user_1"
    eid = "eid_1"

    response = client.post(
        "/api/v1/log/",
        json={
            "eid": eid,
            "user_id": user_id,
            "timestamp": timestamp,
            "event": event,
        },
    )

    assert response.status_code == 200

    message_in_db = schema.Log.find_one()
    assert message_in_db.eid == eid
    assert message_in_db.user_id == user_id
    assert message_in_db.timestamp == datetime.datetime.fromtimestamp(timestamp)
    assert message_in_db.action == event["action"]
    assert message_in_db.element == event["element"]
    assert message_in_db.details == event["details"]
    assert message_in_db.interface == event["interface"]


def test_post_logging_some_inputs(client):
    event = {
        "element": "something",
        "action": "click",
    }
    timestamp = 1000
    eid = "eid_1"

    response = client.post(
        "/api/v1/log/",
        json={
            "eid": eid,
            "event": event,
            "timestamp": timestamp,
        },
    )

    assert response.status_code == 200

    message_in_db = schema.Log.find_one()
    assert message_in_db.eid == eid
    assert message_in_db.user_id is None
    assert message_in_db.timestamp == datetime.datetime.fromtimestamp(timestamp)
    assert message_in_db.action == event.get("action")
    assert message_in_db.element == event.get("element")
    assert message_in_db.details == event.get("details", {})
    assert message_in_db.interface == event.get("interface")
