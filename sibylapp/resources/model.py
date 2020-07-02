import logging

from flask_restful import Resource
from flask import request
from sibylapp.db import schema

from explanation_toolkit import global_explanation

import pandas as pd

LOGGER = logging.getLogger(__name__)


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
            LOGGER.exception('Error getting entity. '
                             'Entity %s does not exist.', model_id)
            return {
                       'message': 'Entity {} does not exist'.format(model_id)
                   }, 400

        return model, 200


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
        models = schema.Model.find()

        return models, 200


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
        # TODO: calculate if not already present
        model_id = request.args.get('model_id', None)
        model = schema.Entity.find_one(id=model_id)

        importances = model.importances
        if importances is None:
            training_set = model.training_set
            data = schema.Entity.find(training_set.entity_ids)
            y = ...
            importances = global_explanation.get_global_importance(model.model, data, y)
        return importances, 200


class Prediction(Resource):
    def get(self):
        """
        @api {get} /prediction/ Get prediction score of an entity
        @apiName GetPrediction
        @apiGroup Model
        @apiVersion 1.0.0
        @apiDescription Get prediction score of a specified entity.

        @apiParam {String} model_id ID of the model to get prediction scores.
        @apiParam {String} entity_id ID of the entity to get prediction scores.

        @apiSuccess {Number} score Prediction score of the entity by the
            specified model.
        """
        model_id = request.args.get('model_id', None)
        entity_id = request.args.get('entity_id', None)

        model = schema.Entity.find_one(id=model_id)

        if model.predictions is None:
            model.predictions = {}

        if entity_id not in model.predictions:
            entity = schema.Entity.find_one(
                id=entity_id)  # load the entity's features
            entity_features = pd.DataFrame.from_dict(entity.features)
            prediction = model.model.predict(entity_features)
            model.predictions[entity_id] = prediction
            model.save()

        prediction = model.predictions[entity_id]

        return prediction, 200
