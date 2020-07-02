import logging

from flask_restful import Resource

from sibylapp.db import schema

LOGGER = logging.getLogger(__name__)


class Feature(Resource):
    def get(self, feature_name):
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
        feature = schema.Feature.find_one(name=feature_name)

        return feature, 200


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
        features = schema.Feature.find()

        return features, 200


class Categories(Resource):
    def get(self):
        """
        @api {get} /categories/ Get category list
        @apiName GetFeatureCategory
        @apiGroup Feature
        @apiVersion 1.0.0
        @apiDescription Get the list of all feature categories.

        @apiSuccess {Object[]} categories List of Category Objects.
        @apiSuccess {String} categories.name Name of category.
        @apiSuccess {String} categories.color Color of category.
        """
        categories = schema.Category.find()
        return categories, 200
