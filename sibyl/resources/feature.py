import logging

from flask import request
from flask_restful import Resource

from sibyl.db import schema

LOGGER = logging.getLogger(__name__)


def get_feature(feature_doc, detailed=False):
    feature = {
        "name": feature_doc.name,
        "description": feature_doc.description,
        "type": feature_doc.type,
        "category": feature_doc.category,
    }
    if detailed:
        feature["values"] = feature_doc.values
        feature["negated_description"] = feature_doc.negated_description
    return feature


def get_category(category_doc):
    category = {
        "name": category_doc.name,
        "color": category_doc.color,
        "abbreviation": category_doc.abbreviation,
    }
    return category


def add_feature(feature, feature_data):
    if "category" in feature_data:
        if schema.Category.find_one(name=feature_data["category"]) is None:
            add_category(None, {"name": feature_data["category"]})
    if feature is None:
        if "type" not in feature_data:
            LOGGER.exception("Error creating feature. Must provide type for new feature")
            return {"message": "Must provide type when adding new feature"}, False
        feature = schema.Feature(**feature_data)
        feature.save()
    else:
        if "type" in feature_data:
            # Prevent validation errors by removing values
            if feature_data["type"] != "categorical":
                feature.values = []
            # Workaround because "type" is a reserved keyword in mongoengine
            feature.type = feature_data.pop("type")
            feature = feature.save()
        if len(feature_data) > 0:
            feature.modify(**feature_data)
            feature = feature.save()
    return feature, True


def add_category(category, category_data):
    if category is None:
        category = schema.Category(**category_data)
        category.save()
    else:
        category.modify(**category_data)
        category.save()
    return category


class Feature(Resource):
    def get(self, feature_name):
        """
        Get a feature by name
        ---
        tags:
          - feature
        parameters:
          - name: feature_name
            in: path
            schema:
              type: string
            required: true
            description: Name of the feature to get info for
        responses:
          200:
            description: Feature information
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Feature'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        feature = schema.Feature.find_one(name=feature_name)
        if feature is None:
            LOGGER.exception("Error getting feature. Feature %s does not exist.", feature_name)
            return {"message": "Feature {} does not exist".format(feature_name)}, 400

        return get_feature(feature, detailed=True), 200

    def put(self, feature_name):
        """
        Update or create a feature by name
        ---
        tags:
          - feature
        parameters:
          - name: feature_name
            in: path
            schema:
              type: string
            required: true
            description: Name of the feature to update
        requestBody:
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FeatureWithoutName'
        responses:
          200:
            description: Feature information
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Feature'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        feature_data = request.json
        feature = schema.Feature.find_one(name=feature_name)
        if feature is None:
            feature_data["name"] = feature_name
        added_feature, success = add_feature(feature, feature_data)
        if not success:
            return added_feature, 400
        else:
            return get_feature(added_feature, detailed=True), 200


class Features(Resource):
    def get(self):
        """
        Get all features
        ---
        tags:
          - feature
        responses:
          200:
            description: All features
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    features:
                      type: array
                      items:
                        $ref: '#/components/schemas/Feature'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        documents = schema.Feature.find()
        try:
            features = [get_feature(document, detailed=True) for document in documents]
        except Exception as e:
            LOGGER.exception(e)
            return {"message": str(e)}, 500
        else:
            return {"features": features}, 200

    def put(self):
        """
        Update or create multiple features
        ---
        tags:
          - feature
        requestBody:
          content:
            application/json:
              schema:
                type: object
                properties:
                  features:
                    type: array
                    items:
                      $ref: '#/components/schemas/Feature'
        responses:
          200:
            description: All added features
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    features:
                      type: array
                      items:
                        $ref: '#/components/schemas/Feature'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        all_feature_data = request.json["features"]
        return_features = []
        for feature_data in all_feature_data:
            if "name" not in feature_data:
                LOGGER.exception("Error creating/modifying feature. Must provide name.")
                return {"message": "Must provide name for all features"}, 400
            feature = schema.Feature.find_one(name=feature_data["name"])
            added_feature, success = add_feature(feature, feature_data)
            if not success:
                return added_feature, 400
            else:
                return_features.append(added_feature)

        return [get_feature(feature, detailed=True) for feature in return_features], 200


class Categories(Resource):
    def get(self):
        """
        Get all feature categories
        ---
        tags:
          - feature
        responses:
          200:
            description: All categories
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    categories:
                      type: array
                      items:
                        $ref: '#/components/schemas/Category'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        documents = schema.Category.find()
        try:
            categories = [get_category(document) for document in documents]
        except Exception as e:
            LOGGER.exception(e)
            return {"message": str(e)}, 500
        else:
            return {"categories": categories}, 200

    def put(self):
        """
        Add or modify categories
        ---
        tags:
          - feature
        requestBody:
          content:
            application/json:
              schema:
                type: object
                properties:
                  categories:
                    type: array
                    items:
                      $ref: '#/components/schemas/Category'
        responses:
          200:
            description: Categories added or modified
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/Category'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        category_data = request.json["categories"]
        return_categories = []
        for category in category_data:
            if "name" not in category:
                LOGGER.exception("Error creating/modifying category. Must provide name.")
                return {"message": "Must provide name for all categories"}, 400
            document = schema.Category.find_one(name=category["name"])
            added_category = add_category(document, category)
            return_categories.append(added_category)
        return [get_category(category) for category in return_categories], 200
