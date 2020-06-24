import logging

from flask_restful import Resource

LOGGER = logging.getLogger(__name__)


class Feature(Resource):
    def get(self):
        """
        @api {get} /features/:feature_name/ Get details of a feature
        @apiName GetFeature
        @apiGroup Feature
        @apiVersion 1.0.0
        @apiDescription Get details of a specific feature.

        @apiSuccess {String} name Name of the feature.
        @apiSuccess {String} description Short paragraph description of 
            the feature.
        @apiSuccess {String} category Category of the feature.
        @apiSuccess {String="numeric","binary","category"} type Value type.
        """
        pass


class Features(Resource):
    def get(self):
        """
        @api {get} /features/ Get all features
        @apiName GetAllFeature
        @apiGroup Feature
        @apiVersion 1.0.0
        @apiDescription Get details about all the features.

        @apiSuccess {Object[]} features List of Feature Objects.
        @apiSuccess {String} features.name Name of the feature.
        @apiSuccess {String} features.description Short paragraph description of 
            the feature.
        @apiSuccess {String} features.category Category of the feature.
        @apiSuccess {String="numeric","binary","category"} features.type 
            Value type of the feature.
        """
        pass


class Categories(Resource):
    def get(self):
        """
        @api {get} /categories/ Get category list
        @apiName GetFeatureCategory
        @apiGroup Feature
        @apiVersion 1.0.0
        @apiDescription Get the list of all feature categories.

        @apiSuccess {String[]} categories List of category names.
        """
        pass
