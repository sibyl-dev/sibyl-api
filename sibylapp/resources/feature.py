import logging

from flask_restful import Resource

from sibylapp.db import schema

LOGGER = logging.getLogger(__name__)


def get_feature(feature_doc):
    feature = {
        'name': feature_doc.name,
        'description': feature_doc.description,
        'type': feature_doc.type
    }
    if feature_doc.category is not None:
        feature['category'] = feature_doc.category.name
    else:
        feature['category'] = None
    return feature


def get_category(category_doc):
    category = {
        'name': category_doc.name,
        'color': category_doc.color
    }
    return category


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
        if feature is None:
            LOGGER.exception('Error getting feature. '
                             'Feature %s does not exist.', feature_name)
            return {'message':
                    'Feature {} does not exist'.format(feature_name)}, 400

        return get_feature(feature), 200


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
        documents = schema.Feature.find()
        try:
            features = [get_feature(document) for document in documents]
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 500
        else:
            return {'features': features}, 200


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
        documents = schema.Category.find()
        try:
            categories = [get_category(document) for document in documents]
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 500
        else:
            return {'categories': categories}
