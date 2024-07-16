import logging
import json
import numpy as np

from flask import request, jsonify
from flask_restful import Resource, reqparse

from sibyl.db import schema

LOGGER = logging.getLogger(__name__)


def get_entity(entity_doc):
    entity = {
        "eid": entity_doc.eid,
        "properties": entity_doc.properties,
    }
    return entity


def get_row(row_doc):
    row = {"row_id": row_doc.row_id, "features": row_doc.features, "label": row_doc.label}
    return row


# def get_entity_row(entity_doc, row_id=None, features=True):
#     entity = {
#         "eid": entity_doc.eid,
#         "property": entity_doc.property,
#     }
#     if features:
#         entity["features"] = entity_doc.features[row_id]
#     return entity


def add_entity(entity, entity_data):
    if entity is None:
        if "row_ids" not in entity_data and "features" in entity_data:
            entity_data["row_ids"] = list(entity_data["features"].keys())
        entity = schema.Entity(**entity_data)
        entity.save()
    else:
        entity.modify(**entity_data)
        entity.save()
    return entity, True


class Entity(Resource):
    def get(self, eid):
        """
        Get an Entity and all its data by ID, optionally filtering by params
        ---
        tags:
          - entity
        parameters:
          - name: eid
            in: path
            schema:
              type: string
            required: true
            description: ID of the entity to get
          - name: timestamp
            in: query
            schema:
              type: string
            required: false
        responses:
          200:
            description: Entity
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Entity'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        entity = schema.Entity.objects(eid=eid).first()
        if entity is None:
            LOGGER.exception("Error getting entity. Entity %s does not exist.", eid)
            return {"message": "Entity {} does not exist".format(eid), "code": 400}, 400

        query_params_str = request.args.get("params", "{}")
        try:
            query_params = json.loads(query_params_str)
        except json.JSONDecodeError:
            return {
                "message": "Invalid params format. Must be a valid JSON object.",
                "code": 400,
            }, 400

            # Ensure the 'eid' is included in the query parameters
        query_params["eid"] = eid

        # Find the rows associated with the entity, filtering by query_params
        rows = schema.Row.objects(__raw__=query_params)
        # Convert rows to a list of dictionaries
        rows_list = [row.to_mongo().to_dict() for row in rows]
        for row in rows_list:
            row.pop("_id", None)

        def replace_nan(obj):
            if isinstance(obj, float) and np.isnan(obj):
                return None
            elif isinstance(obj, dict):
                return {k: replace_nan(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_nan(i) for i in obj]
            else:
                return obj

        rows_list = replace_nan(rows_list)

        # Return the entity and rows as JSON
        return jsonify({"eid": entity["eid"], "rows": rows_list})

    def put(self, eid):
        """
        Modify an Entity by ID
        ---
        tags:
          - entity
        parameters:
          - name: eid
            in: path
            schema:
              type: string
            required: true
            description: ID of the entity to modify/create
        requestBody:
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EntityWithoutEid'
        responses:
          200:
            description: Entity that was modified
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Entity'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        entity_data = request.json

        entity = schema.Entity.find_one(eid=str(eid))
        if entity is None:
            entity_data["eid"] = eid

        added_entity, success = add_entity(entity, entity_data)

        if not success:
            return added_entity, 400
        else:
            return get_entity(added_entity, features=True), 200


class Entities(Resource):
    def __init__(self):
        parser_get = reqparse.RequestParser(bundle_errors=True)
        parser_get.add_argument("group_id", type=str, default=None, location="args")
        self.parser_get = parser_get

    def get(self):
        """
        Get all Entities.
        If group ID is specified, return entities of that group.
        ---
        tags:
          - entity
        parameters:
          - name: group_id
            in: query
            schema:
              type: string
            required: false
            description: ID of the group to filter entities
        responses:
          200:
            description: All entities
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/EntitySimplified'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        try:
            args = self.parser_get.parse_args()
        except Exception as e:
            LOGGER.exception(str(e))
            return {"message", str(e)}, 400

        group_id = args["group_id"]
        if group_id is None:
            # no referral filter applied
            documents = schema.Entity.find()
        else:
            # filter entities by referral ID
            documents = schema.Entity.find(properties__group_ids__contains=group_id)
            if documents is None:
                LOGGER.log(20, "group %s has no entities" % str(group_id))
                return {"message": "group %s has no entities" % str(group_id)}, 400
        try:
            entities = [get_entity(document) for document in documents]
        except Exception as e:
            LOGGER.exception(e)
            return {"message": str(e)}, 500
        else:
            return {"entities": entities}

    def put(self):
        """
        Insert or modify multiple Entities
        ---
        tags:
          - entity
        requestBody:
          content:
            application/json:
              schema:
                type: object
                properties:
                  entities:
                    type: array
                    items:
                      $ref: '#/components/schemas/Entity'
                    description: List of entities to insert or modify
        responses:
          200:
            description: All entities
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/Entity'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        all_entity_data = request.json["entities"]
        return_entities = []
        for entity_data in all_entity_data:
            if "eid" not in entity_data:
                LOGGER.exception("Error creating/modifying entity. Must provide eid.")
                return {"message": "Must provide eid for all entities"}, 400
            entity = schema.Entity.find_one(eid=entity_data["eid"])
            added_entity, success = add_entity(entity, entity_data)
            if not success:
                return added_entity, 400
            else:
                return_entities.append(added_entity)

        return [get_entity(entity, features=True) for entity in return_entities], 200


class Events(Resource):
    def __init__(self):
        parser_get = reqparse.RequestParser(bundle_errors=True)
        parser_get.add_argument("eid", type=str, required=True, location="args")
        self.parser_get = parser_get

    def get(self):
        """
        Get the Events of an Entity
        ---
        tags:
          - entity
        parameters:
          - name: eid
            in: query
            schema:
              type: string
            required: true
            description: ID of the entity to filter events
        responses:
          200:
            description: Events of an entity
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/Event'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """

        try:
            args = self.parser_get.parse_args()
        except Exception as e:
            LOGGER.exception(str(e))
            return {"message", str(e)}, 400

        eid = args["eid"]

        entity = schema.Entity.find_one(eid=eid)
        if entity is None:
            message = "message: Entity {} does not exist".format(eid)
            LOGGER.exception(message)
            return {"message": message, "code": 400}, 400

        return get_events(entity), 200
