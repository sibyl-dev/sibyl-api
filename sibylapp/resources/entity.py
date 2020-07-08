import logging

from flask_restful import Resource
from sibylapp.db import schema
from flask import request

LOGGER = logging.getLogger(__name__)


def __valid_id(val):
    pass
    #if not val:
        #raise ValidationError


def get_outcomes(entity_doc):
    outcomes = []
    for event_doc in entity_doc.outcomes:
        outcomes.append({
            'datetime': event_doc.datetime,
            'type': event_doc.type,
            'property': event_doc.property
        })
    outcomes = {'outcomes': outcomes}
    return outcomes


def get_entity(entity_doc, features=True):
    entity = {
        'eid': entity_doc.eid,
        'property': entity_doc.property,
    }
    if features:
        entity['features'] = entity_doc.features
    return entity


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
        entity = schema.Entity.find_one(eid=str(entity_id))
        if entity is None:
            LOGGER.exception('Error getting entity. '
                             'Entity %s does not exist.', entity_id)
            return {
                       'message': 'Entity {} does not exist'.format(entity_id)
                   }, 400

        return get_entity(entity, features=True), 200


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
        documents = schema.Entity.find()
        try:
            entities = \
                [get_entity(document, features=False) for document in documents]
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 500
        else:
            print(entities)
            return {'entities': entities}


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
        entity_id = request.args.get('entity_id', None)
        entity = schema.Entity.find_one(eid=entity_id)
        if entity is None:
            LOGGER.exception('Error getting entity. '
                             'Entity %s does not exist.', entity_id)
            return {
                       'message': 'Entity {} does not exist'.format(entity_id)
                   }, 400

        outcomes = get_outcomes(entity)
        return outcomes, 200
