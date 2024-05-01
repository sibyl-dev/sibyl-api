import logging

from flask import request
from flask_restful import Resource

from sibyl.db import schema
import datetime

LOGGER = logging.getLogger(__name__)


class Logger(Resource):
    def post(self):
        """
        Save a log message.
        ---
        tags:
            - Logger
        requestBody:
            required: true
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            event:
                                type: object
                                properties:
                                    element:
                                        type: string
                                    action:
                                        type: string
                                    details:
                                        type: object
                                    interface:
                                        type: string
                            timestamp:
                                type: integer
                                description: timestamp in seconds-since-epoch
                            user_id:
                                type: string
                            eid:
                                type: string
        responses:
            200:
                description: Log successful
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                message:
                                    type: string
            400:
                $ref: '#/components/responses/ErrorMessage'
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
