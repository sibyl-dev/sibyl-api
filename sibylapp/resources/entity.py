import logging

from flask_restful import Resource
from sibylapp.db import schema
from flask import request

LOGGER = logging.getLogger(__name__)

# TODO: get_entity(): refer to MTV's get_signal()

class Entity(Resource):
    def get(self, entity_id):
        """
        @api {get} /entities/:entity_id/ Get an entity by ID
        @apiName GetEntity
        @apiGroup Entity
        @apiVersion 1.0.0
        @apiDescription Get the detailed information of an entity.

        @apiSuccess {String} id ID of the entity.
        @apiSuccess {Object[]} features List of features.
        @apiSuccess {String} features.name  Feature name.
        @apiSuccess {Number|String} features.value Feature value.
        @apiSuccess {Object} [property] Special property of this entity.
        @apiSuccess {String} [property.name] Name of the entity.
        @apiSuccess {String[]} [property.case_ids] IDs of cases the entity
                                         is involved in.

        @apiSuccessExample {json} Success-Response:
            HTTP/1.1 200 OK
            {
                "id": "18",
                "features": [
                    {"name": "f1", "value": "v1"},
                    ... 
                    {"name": "fn", "value": "vn"}
                ],
                "property": {
                    "name": "Elsa",
                    "case_ids": ["ca19", "ca88", "ca133"]
                } 
            }
        """
        #http://localhost:3000/api/v1/entities/balalala/
        # TODO: format validation for entity_id (ensure string)
        entity = schema.Entity.find_one(eid=entity_id)
        if entity is None:
            LOGGER.exception('Error getting entity. '
                             'Entity %s does not exist.', entity_id)
            return {
                       'message': 'Entity {} does not exist'.format(entity_id)
                   }, 400

        # TODO: use get_entity
        return entity, 200


class Entities(Resource):
    def get(self):
        """
        @api {get} /entities/ Get all entities meta info
        @apiName GetEntities
        @apiGroup Entity
        @apiVersion 1.0.0
        @apiDescription Get meta information of all the entities.

        @apiSuccess {Object[]} entities List of entities.
        @apiSuccess {String} entities.id ID of the entity.
        @apiSuccess {Object} [entities.property] ID of the entity.
        @apiSuccess {String} [entities.property.name] Name of the entity.
        """
        entities = schema.Entity.find()
        # TODO: add error checking
        # TODO: use [get_entity()], refer to MTV
        return entities, 200


class Outcome(Resource):
    def get(self):
        """
        @api {get} /outcome/ Get the outcome of an entity
        @apiName GetOutcome
        @apiGroup Entity
        @apiVersion 1.0.0
        @apiDescription Get the history/outcome of a entity.

        @apiParam {String} [entity_id] Id of the entity.

        @apiSuccess {Object[]} History/Outcomes List of Outcome Objects. TODO
        """
        #http://localhost:3000/api/v1/outcome/?entity_id=balalala&param2=balalalal&param3=baba
        entity_id = request.args.get('entity_id', None)
        entity = schema.Entity.find_one(id=entity_id)
        if entity is None:
            LOGGER.exception('Error getting entity. '
                             'Entity %s does not exist.', entity_id)
            return {
                       'message': 'Entity {} does not exist'.format(entity_id)
                   }, 400

        # TODO: convert to dictionary, convert events
        outcomes = entity.outcomes
        return outcomes, 200
