import os


def test_post_logging(client):
    event = {
        "element": "something",
        "action": "click",
        "details": "done"
    }
    timestamp = "1000"
    user_id = "user_1"
    eid = "eid_1"

    response = client.post('/api/v1/logging/',
                           json={"eid": eid, "user_id": user_id, "timestamp": timestamp,
                                 "event": event}).json

    assert response["message"] == "log successful"

    log_file = open("test.csv")
    assert log_file.readline().strip() == \
        "timestamp,user_id,eid,event_element,event_action,event_details"
    assert log_file.readline().strip() == \
        ",".join((timestamp, user_id, eid, event["element"], event["action"], event["details"])) \
        + ","

    os.remove("test.csv")
