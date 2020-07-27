import logging

from flask import request
from flask_restful import Resource
import time
import json
from sibylapp.utils import read_config

LOGGER = logging.getLogger(__name__)


def format_message(message):
    s = ""
    for key in message:
        s += key
        s += ": "
        s += message[key]
        s += "\n"
    s += "\n"
    return s


class Logging(Resource):
    def post(self):
        """
        @api {post} /logging/ Save a log message
        @apiName PostLogging
        @apiGroup Logging
        @apiVersion 1.0.0
        @apiDescription Save information to the log.

        @apiParam {String} log_message Message to add to log
        @apiParam {String} user_id Id of user using the app

        @apiSuccess {String} timestamp Timestamp added to log
        """
        timestamp = str(time.time())
        body = request.json
        log_message = body.get("log_message")
        if log_message is None:
            LOGGER.warning('No message provided')
            log_message = ""

        try:
            log_message = str(log_message)
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 400

        user_id = body.get("user_id")
        if user_id is None:
            user_id = ""

        try:
            user_id = str(user_id)
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 400

        full_message = {"user": user_id,
                        "timestamp": timestamp,
                        "message": log_message}

        config = read_config('./sibylapp/config.yaml')
        log_file = config["log_filename"]
        try:
            with open(log_file, "a+") as f:
                f.write(format_message(full_message))
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 400

        return {"timestamp":timestamp}
