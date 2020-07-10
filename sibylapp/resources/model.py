import logging

from flask_restful import Resource
from flask import request
from sibylapp.db import schema

import pickle
import pandas as pd


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
        @api {get} /models/:model_id/ Get metadata of a model
        @apiName GetModel
        @apiGroup Model
        @apiVersion 1.0.0
        @apiDescription Get the metadata of a model.

        @apiSuccess {String} id ID of the model.
        @apiSuccess {String} name Name of the model.
        @apiSuccess {String} description Short paragraph description of
            model functionality.
        @apiSuccess {String} performance Short paragraph description of 
            model performance
        """
        model = schema.Model.find_one(id=model_id)
        if model is None:
            LOGGER.exception('Error getting model. '
                             'Model %s does not exist.', model_id)
            return {
                       'message': 'Model {} does not exist'.format(model_id)
                   }, 400

        return get_model(model, basic=False), 200


class Models(Resource):
    def get(self):
        """
        @api {get} /models/ Get metadata of all models
        @apiName GetModels
        @apiGroup Model
        @apiVersion 1.0.0
        @apiDescription Return all model metadatas with model IDs and names.

        @apiSuccess {Object[]} models List of Model Object.
        @apiSuccess {String} models.id ID of the model.
        @apiSuccess {String} models.name Name of the model.
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
        @api {get} /importance/ Get global feature importance of a model
        @apiName GetFeatureImportance
        @apiGroup Model
        @apiVersion 1.0.0
        @apiDescription Get the importances of all features of a specified model.

        @apiParam {String} model_id ID of the model to get feature importances.

        @apiSuccess {Object} importances Feature importance object.
        @apiSuccess {Number} importances.[key] Importance value of the feature [key].
        """
        model_id = request.args.get('model_id', None)
        model = schema.Model.find_one(id=model_id)
        if model is None:
            LOGGER.exception('Error getting model. '
                             'Model %s does not exist.', model_id)
            return {
                       'message': 'Model {} does not exist'.format(model_id)
                   }, 400

        importances = model.importances
        return {'importances': importances}


class Prediction(Resource):
    def get(self):
        """
        @api {get} /prediction/ Get prediction of an entity
        @apiName GetPrediction
        @apiGroup Model
        @apiVersion 1.0.0
        @apiDescription Get prediction of a specified entity.

        @apiParam {String} model_id ID of the model to get prediction.
        @apiParam {String} eid ID of the entity to get prediction.

        @apiSuccess {Number} output Prediction of the entity by the
            specified model.
        """
        model_id = request.args.get('model_id', None)
        eid = request.args.get('eid', None)

        entity = schema.Entity.find_one(eid=eid)
        entity_features = pd.DataFrame(entity.features, index=[0])

        model_doc = schema.Model.find_one(id=model_id)
        if model_doc is None:
            LOGGER.exception('Error getting model. '
                             'Model %s does not exist.', model_id)
            return {
                       'message': 'Model {} does not exist'.format(model_id)
                   }, 400
        model_bytes = model_doc.model
        try:
            model = pickle.loads(model_bytes)
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 500
        prediction = model.predict(entity_features)[0]
        return {"output": prediction}, 200
