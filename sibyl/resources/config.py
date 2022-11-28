import logging

from flask_restful import Resource, reqparse

from sibyl.db import schema

LOGGER = logging.getLogger(__name__)


def get_config(config_doc):
    config = {
        'id': str(config_doc.id),
        'terms': config_doc.terms,
        'pos_color': config_doc.pos_color,
        'neg_color': config_doc.neg_color,
    }
    return config


def get_config_id(config_doc):
    config = {
        'id': str(config_doc.config_id),
    }
    return config


class Config(Resource):
    def get(self, config_id):
        """
        Get a configuration by ID
        ---
        tags:
          - config
        security:
          - tokenAuth: []
        parameters:
          - name: config_id
            in: path
            schema:
              type: string
            required: true
            description: ID of the configuration to get
        responses:
          200:
            description: Configuration to be returned
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Config'
                  externalJson:
                    summary: external example
                    externalValue: '/examples/config-get-200.json'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        config = schema.Config.find_one(id=str(config_id))
        if config is None:
            LOGGER.exception('Error getting config. '
                             'Config %s does not exist.', config_id)
            return {
                'message': 'Config {} does not exist'.format(config_id),
                'code': 400
            }, 400

        return get_config(config), 200


class Configs(Resource):
    def get(self):
        """
        Get all Configs
        ---
        tags:
          - config
        security:
          - tokenAuth: []
        responses:
          200:
            description: Get all configs
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    models:
                      type: array
                      items:
                        $ref: '#/components/schemas/Configs'
                examples:
                  externalJson:
                    summary: external example
                    externalValue: '/examples/configs-get-200.json'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        documents = schema.Config.find()
        try:
            configs = [get_config_id(document) for document in documents]
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 500
        else:
            return {'models': configs}, 200
