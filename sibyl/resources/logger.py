import logging

from flask import request
from flask_restful import Resource

from sibyl import g

LOGGER = logging.getLogger(__name__)

log_headers = [
    "timestamp",
    "user_id",
    "eid",
    "event_element",
    "event_action",
    "event_details",
]


def format_message(event):
    """
    Formats as csv row
    :param event: dictionary of event components
    :return: formatted string for saving
    """
    s = ""
    for header in log_headers:
        s += str(event[header])
        s += ","

    s += "\n"
    return s


class Logger(Resource):
    def post(self):
        """
        @api {post} /logging/ Save a log message
        @apiName PostLogging
        @apiGroup Logger
        @apiVersion 1.0.0
        @apiDescription Save information to the log.

        @apiParam {Object} event Details of event to log
        @apiParam {String} event.element Element that was interacted with
        @apiParam {String="click", "type", "filter"} event.action
                  click=clicked on button, type=filled in textbox,
                  filter=filtered a table)
        @apiParam {String} event.details Details of event
                  (text that was put in textbox, filter that was selected)
        @apiParam {Float} timestamp Timestamp of the event in seconds since
                                    Epoch
        @apiParam {String} user_id Id of user using the app
        @apiParam {String} eid Id of entity involved
        """
        body = request.json

        user_id = body.get("user_id")
        if user_id is None:
            user_id = ""
        try:
            user_id = str(user_id)
        except Exception as e:
            LOGGER.exception(e)
            return {"message": str(e)}, 400

        eid = body.get("eid")
        if eid is None:
            eid = ""
        try:
            eid = str(eid)
        except Exception as e:
            LOGGER.exception(e)
            return {"message": str(e)}, 400

        timestamp = body.get("timestamp")
        if timestamp is None:
            LOGGER.exception("Must provide timestamp to log")
            return {"Must provide timestamp to log"}, 400
        try:
            timestamp = int(timestamp)
        except Exception as e:
            LOGGER.exception(e)
            return {"message": str(e)}, 400

        event = body.get("event")
        if event is None:
            LOGGER.exception("Must provide event to log")
            return {"Must provide event to log"}, 400
        if "element" not in event:
            LOGGER.exception("Event must have element")
            return {"Event must have element"}, 400
        if "action" not in event:
            LOGGER.exception("Event must have action")
            return {"Event must have action"}, 400

        event_element = event["element"]
        event_action = event["action"]
        if "details" in event:
            event_details = event["details"]
        else:
            event_details = ""

        full_message = {
            "user_id": user_id,
            "eid": eid,
            "timestamp": timestamp,
            "event_element": event_element,
            "event_action": event_action,
            "event_details": event_details,
        }
        log_file = g["config"]["log_filename"]
        try:
            with open(log_file, "a+") as f:
                if f.tell() == 0:
                    f.write(",".join(log_headers))
                    f.write("\n")
                f.write(format_message(full_message))
        except Exception as e:
            LOGGER.exception(e)
            return {"message": str(e)}, 400

        return {"message": "log successful"}, 200
