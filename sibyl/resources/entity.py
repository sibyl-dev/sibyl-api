import logging

from flask import request
from flask_restful import Resource, reqparse

from sibyl.db import schema

LOGGER = logging.getLogger(__name__)


def get_events(entity_doc):
    events = []
    for event_doc in entity_doc.events:
        events.append({
            "event_id": event_doc.event_id,
            "datetime": str(event_doc.datetime),
            "type": event_doc.type,
            "property": event_doc.property,
        })
    events = {"events": events}
    return events


def get_entity(entity_doc, features=True):
    entity = {
        "eid": entity_doc.eid,
        "row_ids": entity_doc.row_ids,
        "property": entity_doc.property,
    }
    if features:
        entity["features"] = entity_doc.features
    if "labels" in entity_doc:
        entity["labels"] = entity_doc.labels
    return entity


def get_entity_row(entity_doc, row_id=None, features=True):
    entity = {
        "eid": entity_doc.eid,
        "property": entity_doc.property,
    }
    if features:
        entity["features"] = entity_doc.features[row_id]
    return entity


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
        Get an Entity by ID
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
          - name: row_id
            in: query
            schema:
              type: string
            description: ID of the row to get for the entity
        responses:
          200:
            description: Entity to be returned
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Entity'
                example:
                  eid: "123"
                  features: {"row_1": {"f1": 10, "f2": 20}, "row_2": {"f1": 20, "f2": 30}}
                  row_ids: ["row_1", "row_2"]
                  labels: {"row_1": 1, "row_2": 0}
                  property: {"group_id": "group_1"}
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        row_id = request.args.get("row_id", None)

        entity = schema.Entity.find_one(eid=str(eid))
        if entity is None:
            LOGGER.exception("Error getting entity. Entity %s does not exist.", eid)
            return {"message": "Entity {} does not exist".format(eid), "code": 400}, 400

        if row_id is None:
            return get_entity(entity, features=True), 200
        return get_entity_row(entity, row_id, features=True), 200

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
        Get all Entities
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
            try:
                entities = [get_entity(document, features=False) for document in documents]
            except Exception as e:
                LOGGER.exception(e)
                return {"message": str(e)}, 500
            else:
                return {"entities": entities}
        else:
            # filter entities by referral ID
            entities = schema.Entity.find(property__group_ids__contains=group_id)
            if entities is None:
                LOGGER.log(20, "group %s has no entities" % str(group_id))
                return []
            return [document.eid for document in entities], 200

    def put(self):
        """
        Insert or modify multiple entities
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
