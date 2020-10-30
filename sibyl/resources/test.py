import logging

from flask import request
from flask_restful import Resource

LOGGER = logging.getLogger(__name__)


class Test(Resource):
    def get(self):
        """
        Refer to ./apidocs/resources/test/get.yml
        """

        return {
            'code': 200,
            'message': 'GET test succeeded',
            'data': request.args
        }, 200

    def post(self):
        """
        Refer to ./apidocs/resources/test/post.yml
        """

        return {
            'code': 200,
            'message': 'POST test succeeded',
            'data': request.json
        }, 200

    def delete(self):
        """
        Refer to ./apidocs/resources/test/delete.yml
        """

        return {
            'code': 200,
            'message': 'DELETE test succeeded'
        }, 200

    def put(self):
        """
        Refer to ./apidocs/resources/test/put.yml
        """

        data = request.json
        if (type(data['item1']) != str) or (type(data['item2']) != str):
            return {
                'code': 400,
                'message': 'invalid arguments - item1 & item2 should be string'
            }

        return {
            'code': 200,
            'message': 'PUT test succeeded'
        }, 200
