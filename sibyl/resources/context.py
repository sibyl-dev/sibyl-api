from logging import getLogger

from flask import request
from flask_restful import Resource

from sibyl.db import schema

LOGGER = getLogger(__name__)


def get_context(context_doc):
    context = {
        "context_id": str(context_doc.context_id),
        "config": context_doc.config,
    }
    return context


def get_context_id(context_doc):
    context = {
        "context_id": str(context_doc.context_id),
    }
    return context


class Context(Resource):
    def get(self, context_id):
        """
        Get a Context by ID
        ---
        tags:
          - context
        parameters:
          - name: context_id
            in: path
            schema:
              type: string
            required: true
            description: ID of the context to get
        responses:
          200:
            description: Context to be returned
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Context'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        context = schema.Context.find_one(context_id=str(context_id))
        if context is None:
            LOGGER.exception("Error getting context. Context %s does not exist.", context_id)
            return {
                "message": "Context {} does not exist".format(context_id),
                "code": 400,
            }, 400

        return {"context": get_context(context)}, 200

    def put(self, context_id):
        """
        Update or create a context
        ---
        tags:
          - context
        parameters:
          - name: context_id
            in: path
            schema:
              type: string
            description: ID of the context to update/create
            required: true
        requestBody:
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Context'
        responses:
          200:
            description: Information about update model
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Context'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        config_data = request.json
        context = schema.Context.find_one(context_id=context_id)
        if context is None:
            context = schema.Context(context_id=context_id, config=config_data)
            context.save()
        else:
            context.config.update(config_data)
            context = context.save()
        return {"context": get_context(context)}, 200


class Contexts(Resource):
    def get(self):
        """
        Get all Context ids
        ---
        tags:
          - context
        responses:
          200:
            description: Get all contexts
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    contexts:
                      type: array
                      items:
                        $ref: '#/components/schemas/Context'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        documents = schema.Context.find()
        try:
            contexts = [get_context_id(document) for document in documents]
        except Exception as e:
            LOGGER.exception(e)
            return {"message": str(e)}, 500
        else:
            return {"contexts": contexts}, 200
