import logging

from flask_restful import Resource

LOGGER = logging.getLogger(__name__)


class Model(Resource):
    def get(self):
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
        pass


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
        pass


class Importance(Resource):
    def get(self):
        """
        @api {get} /importance/ Get global feature importance of a model
        @apiName GetFeatureImportance
        @apiGroup Model
        @apiVersion 1.0.0
        @apiDescription Get the importances of all features of a specified model.

        @apiParam {String} id ID of the model to get feature importances.

        @apiSuccess {Object} importances Feature importance object.
        @apiSuccess {Number} importances.[key] Importance value of the feature [key].
        """
        pass


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
        pass
