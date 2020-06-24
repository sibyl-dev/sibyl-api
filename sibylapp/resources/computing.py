import logging

from flask_restful import Resource

LOGGER = logging.getLogger(__name__)


class Similarentities(Resource):
    def get(self):
        """
        @api {get} /similar_entities/ Get similar entities
        @apiName GetSimilarentities
        @apiGroup Computing
        @apiVersion 1.0.0
        @apiDescription Get a list of similar entities.

        @apiParam {String} entity_id ID of the entity.
        @apiParam {Number} number Number of similar entities to search for.

        @apiSuccess {String[]} entities List of entity IDs.
        """
        pass


class SingleChangePredictions(Resource):
    def post(self):
        """
        @api {post} /single_change_predictions/ Post single prediction 
        @apiName PostSinglePrediction
        @apiGroup Computing
        @apiVersion 1.0.0
        @apiDescription Get the list of updated predictions after making 
        single changes.

        @apiParam {String} entity_id ID of entity to predict on.
        @apiParam {String} model_id ID of model to use for predictions.
        @apiParam {2-Tuple[]} changes List of features to change and 
            their new values.
        @apiParam {String} changes.item1 Name of the feature to change.
        @apiParam {String} changes.item2 Changed Value of the feature.

        @apiSuccess {2-Tuple[]} changes List of features to change and 
            their new values.
        @apiSuccess {String} changes.item1 Name of the feature to change.
        @apiSuccess {String} changes.item2 New prediction of the feature.
        """
        pass


class ModifiedPrediction(Resource):
    def post(self):
        """
        @api {post} /modified_prediction/ Post multiple prediction 
        @apiName PostMultiplePrediction
        @apiGroup Computing
        @apiVersion 1.0.0
        @apiDescription  Get the modified prediction under different conditions

        @apiParam {String} entity_id ID of entity to predict on.
        @apiParam {String} model_id ID of model to use for predictions.
        @apiParam {2-Tuple[]} changes List of features to change and 
            their new values.
        @apiParam {String} changes.item1 Name of the feature to change.
        @apiParam {String} changes.item2 Changed Value of the feature.

        @apiSuccess {Number} prediction New prediction after making
            the requested changes.
        """
        pass


class FeatureDistributions(Resource):
    def post(self):
        """
        @api {post} /modified_prediction/ Get feature distributions 
        @apiName GetFeatureDistributions
        @apiGroup Computing
        @apiVersion 1.0.0
        @apiDescription Get the distributions of all features

        @apiParam {Number} prediction Prediction Prediction to look at distributions for.
        @apiParam {String} id ID of model to use for predictions.

        @apiSuccess {Object[]} distributions Information about the distributions of each
            feature for each feature.
        """
        pass


class FeatureContributions(Resource):
    def post(self):
        """
        @api {get} /computing/contributions/ Get feature contributions 
        @apiName GetFeatureContributions
        @apiGroup Computing
        @apiVersion 1.0.0
        @apiDescription  get the contributions of all features

        @apiParam {String} entity_id ID of the entity to compute.
        @apiParam {String} model ID of the model to compute.

        @apiSuccess {Object} contributions Feature contribution object (key-value pair).
        @apiSuccess {Number} contributions.[key] Contribution value of the feature [key].
        """
        pass
