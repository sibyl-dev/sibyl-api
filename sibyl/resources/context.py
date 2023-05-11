import logging

from flask_restful import Resource, reqparse

from sibyl.db import schema

LOGGER = logging.getLogger(__name__)


def get_context(context_doc):
    context = {
        "id": str(context_doc.id),
        "terms": context_doc.terms,
        "pos_color": context_doc.pos_color,
        "neg_color": context_doc.neg_color,
    }
    return context


def get_context_id(context_doc):
    context = {
        "id": str(context_doc.id),
    }
    return context


class Context(Resource):
    def get(self, context_id):
        """
        Get a context by ID
        ---
        tags:
          - context
        security:
          - tokenAuth: []
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
                  externalJson:
                    summary: external example
                    externalValue: '/examples/context-get-200.json'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        context = schema.Context.find_one(id=str(context_id))
        if context is None:
            LOGGER.exception("Error getting context. Context %s does not exist.", context_id)
            return {
                "message": "Context {} does not exist".format(context_id),
                "code": 400,
            }, 400

        return {"context": get_context(context)}, 200


class Contexts(Resource):
    def get(self):
        """
        Get all Contexts
        ---
        tags:
          - context
        security:
          - tokenAuth: []
        responses:
          200:
            description: Get all contexts
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    models:
                      type: array
                      items:
                        $ref: '#/components/schemas/Contexts'
                examples:
                  externalJson:
                    summary: external example
                    externalValue: '/examples/contexts-get-200.json'
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
