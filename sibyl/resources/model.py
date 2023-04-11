import logging

import pandas as pd
from flask import request
from flask_restful import Resource

from sibyl.db import schema
from sibyl import helpers
import pickle

LOGGER = logging.getLogger(__name__)


def get_model(model_doc, basic=True):
    model = {
        'id': str(model_doc.id),
        'name': model_doc.name
    }
    if not basic:
        model['description'] = model_doc.description
        model['performance'] = model_doc.performance
    return model


class Model(Resource):
    def get(self, model_id):
        """
        Get a Model by ID
        ---
        tags:
          - model
        security:
          - tokenAuth: []
        parameters:
          - name: model_id
            in: path
            schema:
              type: string
            required: true
            description: ID of the model to get information about
        responses:
          200:
            description: Information about the model
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Model'
                examples:
                  externalJson:
                    summary: external example
                    externalValue: '/examples/model-get-200.json'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        model = schema.Model.find_one(id=model_id)
        if model is None:
            LOGGER.exception('Error getting model. Model %s does not exist.', model_id)
            return {
                'message': 'Model {} does not exist'.format(model_id)
            }, 400

        return get_model(model, basic=False), 200


class Models(Resource):
    def get(self):
        """
        Get all Models
        ---
        tags:
          - model
        security:
          - tokenAuth: []
        responses:
          200:
            description: All models
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    models:
                      type: array
                      items:
                        $ref: '#/components/schemas/Model_Partial'
                examples:
                  externalJson:
                    summary: external example
                    externalValue: '/examples/models-get-200.json'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        documents = schema.Model.find()
        try:
            model = [get_model(document, basic=True) for document in documents]
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 500
        else:
            return {'models': model}, 200


class Importance(Resource):
    def get(self):
        """
        Get a Model by ID
        ---
        tags:
          - model
        security:
          - tokenAuth: []
        parameters:
          - name: model_id
            in: path
            schema:
              type: string
            required: true
            description: ID of the model to get importances for
        responses:
          200:
            description: Feature importance for the model
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    importances:
                      type: array
                      items:
                        importance:
                            feature:
                                type: string
                            importance:
                                type: float
                examples:
                  externalJson:
                    summary: external example
                    externalValue: '/examples/importance-get-200.json'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        model_id = request.args.get('model_id', None)
        model = schema.Model.find_one(id=model_id)
        if model is None:
            LOGGER.exception('Error getting model. Model %s does not exist.', model_id)
            return {
                'message': 'Model {} does not exist'.format(model_id)
            }, 400

        importances = model.importances
        return {'importances': importances}


class Prediction(Resource):
    def get(self):
        """
        Get a prediction using the model
        ---
        tags:
          - model
        security:
          - tokenAuth: []
        parameters:
          - name: model_id
            in: query
            schema:
              type: string
            required: true
            description: ID of the model to use to predict
          - name: eid
            in: query
            schema:
              type: string
            required: true
            description: ID of the entity to predict on
        responses:
          200:
            description: Prediction
            content:
              application/json:
                schema:
                  type: number
                examples:
                  inlineJson:
                    summary: inline example
                    value: 10.0
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        model_id = request.args.get('model_id', None)
        eid = request.args.get('eid', None)

        entity = schema.Entity.find_one(eid=eid)
        if entity is None:
            LOGGER.exception('Error getting entity. Entity %s does not exist.', eid)
            return {'message': 'Entity {} does not exist'.format(eid)}, 400
        entity_features = pd.DataFrame(entity.features, index=[0])

        model_doc = schema.Model.find_one(id=model_id)
        if model_doc is None:
            LOGGER.exception('Error getting model. Model %s does not exist.', model_id)
            return {'message': 'Model {} does not exist'.format(model_id)}, 400
        explainer_bytes = model_doc.explainer
        if explainer_bytes is None:
            LOGGER.exception('Model %s explainer has not been trained. ', model_id)
            return {'message': 'Model {} does not have trained explainer'
                           .format(model_id)}, 400
        try:
            explainer = pickle.loads(explainer_bytes)
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 500

        prediction = explainer.model_predict(entity_features)[0].tolist()
        return {"output": prediction}, 200
