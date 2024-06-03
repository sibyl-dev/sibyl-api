import datetime
import logging

from flask import request
from flask_restful import Resource

from sibyl.db import schema

LOGGER = logging.getLogger(__name__)


class Logger(Resource):
    def post(self):
        """
        Save a log message.
        ---
        tags:
          - logging
        requestBody:
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            user_id:
                                type: string
                                description: The id of the user performing the action
                            eid:
                                type: string
                                description: The id of the entity being acted upon
                            timestamp:
                                type: integer
                                description: The time the event occurred, in seconds since the epoch
                            event:
                                type: object
                                properties:
                                    element:
                                        type: string
                                        description: The UI element being acted on
                                    action:
                                        type: string
                                        description: The type of action being performed
                                    details:
                                        type: object
                                        description: Additional details about the event (key:value)
                                    interface:
                                        type: string
                                        description: The interface or page on which the action is
                                                     taken
                                description: The details of the event being logged
                        required:
                          - timestamp
        responses:
            200:
                description: Log successful
            400:
                description: Bad request
        """

        body = request.json

        user_id = body.get("user_id")
        if user_id is not None:
            try:
                user_id = str(user_id)
            except Exception as e:
                LOGGER.exception(e)
                return {"message": str(e)}, 400

        eid = body.get("eid")
        if eid is not None:
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
            event = {}

        full_message = {
            "user_id": user_id,
            "eid": eid,
            "timestamp": datetime.datetime.fromtimestamp(timestamp),
            "element": event.get("element", None),
            "action": event.get("action", None),
            "details": event.get("details", None),
            "interface": event.get("interface", None),
        }
        log_line = schema.Log(**full_message)
        log_line.save()

        return {"message": "log successful"}, 200
