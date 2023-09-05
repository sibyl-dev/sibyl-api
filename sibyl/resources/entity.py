import logging

from flask_restful import Resource, reqparse
from flask import request

from sibyl.db import schema
from mongoengine.queryset.visitor import Q

LOGGER = logging.getLogger(__name__)


def get_events(entity_doc):
    events = []
    for event_doc in entity_doc.events:
        events.append(
            {
                "event_id": event_doc.event_id,
                "datetime": str(event_doc.datetime),
                "type": event_doc.type,
                "property": event_doc.property,
            }
        )
    events = {"events": events}
    return events


def get_entity_row(entity_doc, features=True):
    entity = {
        "eid": entity_doc.eid,
        "row_id": entity_doc.row_id,
        "property": entity_doc.property,
        "label": entity_doc.label,
    }
    if features:
        entity["features"] = entity_doc.features
    return entity


def get_entity(queryset, features=True):
    entity = {"eid": queryset.first().eid}
    row_ids = []
    feature_dict = {}
    label_dict = {}
    for entity_doc in queryset:
        row_ids.append(entity_doc.row_id)
        label_dict[entity_doc.row_id] = entity_doc.label
        if features:
            feature_dict[entity_doc.row_id] = entity_doc.features
    entity["row_ids"] = row_ids
    entity["labels"] = label_dict
    if features:
        entity["features"] = feature_dict
    return entity


class Entity(Resource):
    def get(self, eid):
        """
        Get an Entity by ID
        ---
        tags:
          - entity
        security:
          - tokenAuth: []
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
            description: ID of the row to get
        responses:
          200:
            description: Entity to be returned
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Entity'
                examples:
                  inlineJson:
                    summary: inline example
                    value: {
                        "eid": "18",
                        "features": [
                            {
                                "name": "f1",
                                "value": "v1"
                            }
                        ],
                        "property": {
                            "name": "Elsa",
                            "referral_ids": [
                                "ca19",
                                "ca88",
                                "ca133"
                            ]
                        }
                  }
                  externalJson:
                    summary: external example
                    externalValue: '/examples/entity-get-200.json'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        row_id = request.args.get("row_id", None)

        if row_id is not None:
            entity = schema.Entity.objects(Q(eid=str(eid)) & Q(row_id=str(row_id))).first()
        else:
            entity = schema.Entity.objects(eid=str(eid))
        if entity is None:
            LOGGER.exception(
                "Error getting entity. Entity %s or row id %s does not exist.", (eid, row_id)
            )
            return {
                "message": "Entity {} or row id {} does not exist".format(eid, row_id),
                "code": 400,
            }, 400
        if row_id is None:
            return get_entity(entity), 200
        return get_entity_row(entity, features=True), 200


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
        security:
          - tokenAuth: []
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
                        $ref: '#/components/schemas/Entity'
                examples:
                  externalJson:
                    summary: external example
                    externalValue: '/examples/entities-get-200.json'
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
        security:
          - tokenAuth: []
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
