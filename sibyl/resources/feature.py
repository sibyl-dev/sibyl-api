import logging

from flask_restful import Resource
from flask import request

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


class Feature(Resource):
    def get(self, feature_name):
        """
        Get a feature by name
        ---
        tags:
          - feature
        security:
          - tokenAuth: []
        parameters:
          - name: feature_name
            in: path
            schema:
              type: string
            required: true
            description: Name of the feature to get info for
        responses:
          200:
            description: Feature importance for the model
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Feature'
                examples:
                  externalJson:
                    summary: external example
                    externalValue: '/examples/feature-get-200.json'
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
        Update a feature by name
        ---
        tags:
          - feature
        security:
          - tokenAuth: []
        parameters:
          - name: feature_name
            in: path
            schema:
              type: string
            required: true
            description: Name of the feature to update
        requestBody:
          description: Feature object to update
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
            if "type" not in feature_data:
                LOGGER.exception("Error creating feature. Must provide type for new feature")
                return {"message": "Must provide type when adding new feature"}, 400
            feature_data["name"] = feature_name
            feature = schema.Feature(**feature_data)
            feature.save()
        else:
            feature.modify(**feature_data)
            feature = feature.save()

        return get_feature(feature, detailed=True), 200


class Features(Resource):
    def get(self):
        """
        Get all Features
        ---
        tags:
          - feature
        security:
          - tokenAuth: []
        responses:
          200:
            description: All features
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/Feature'
                examples:
                  externalJson:
                    summary: external example
                    externalValue: '/examples/features-get-200.json'
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


class Categories(Resource):
    def get(self):
        """
        Get all Categories
        ---
        tags:
          - feature
        security:
          - tokenAuth: []
        responses:
          200:
            description: All categories
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/Category'
                examples:
                  externalJson:
                    summary: external example
                    externalValue: '/examples/categories-get-200.json'
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
