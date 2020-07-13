import logging

from flask import request
from flask_restful import Resource

LOGGER = logging.getLogger(__name__)


class Test(Resource):
    def get(self, param1):
        """
        @api {get} /test/:param1/ Get test
        @apiName GetTest
        @apiGroup Test
        @apiVersion 1.0.0
        @apiDescription Get test.

        @apiParam {String} param2 Param2.
        """
        param2 = request.args.get('param2', None)
        return {
            'param1': param1,
            'param2': param2
        }, 200

    def post(self, param1):
        """
        @api {post} /test/:param1/ Post test
        @apiName PostTest
        @apiGroup Test
        @apiVersion 1.0.0
        @apiDescription Post test.

        @apiParam {String} param2 Param2.
        """
        #http://localhost:3000/api/v1/test/12321/
        #body
        if request.json is not None:
            body = request.json
        else:
            body = dict()

        param2 = body.get('param2', None)

        return {
            'param1': param1,
            'param2': param2
        }, 200

        pass
