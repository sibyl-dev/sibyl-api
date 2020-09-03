import logging

from flask import request
from flask_restful import Resource

from sibylapp.db import schema

LOGGER = logging.getLogger(__name__)


def get_events(entity_doc):
    events = []
    for event_doc in entity_doc.events:
        events.append({
            'event_id': event_doc.event_id,
            'datetime': str(event_doc.datetime),
            'type': event_doc.type,
            'property': event_doc.property
        })
    events = {'events': events}
    return events


def get_entity(entity_doc, features=True):
    entity = {
        'eid': entity_doc.eid,
        'property': entity_doc.property,
    }
    if features:
        entity['features'] = entity_doc.features
    return entity


def get_case(case_doc):
    case = {
        'case_id': case_doc.case_id,
        'property': case_doc.property
    }
    return case


class Entity(Resource):
    def get(self, eid):
        """
        @api {get} /entities/:eid/ Get an entity by ID
        @apiName GetEntity
        @apiGroup Entity
        @apiVersion 1.0.0
        @apiDescription Get the detailed information of an entity.

        @apiSuccess {String} eid ID of the entity.
        @apiSuccess {Object[]} features List of features.
        @apiSuccess {String} features.name  Feature name.
        @apiSuccess {Number|String} features.value Feature value.
        @apiSuccess {Object} [property] Special property of this entity.
        @apiSuccess {String[]} [property.case_ids] IDs of cases the entity
                                         is involved in.

        @apiSuccessExample {json} Success-Response:
            HTTP/1.1 200 OK
            {
                "eid": "18",
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
        entity = schema.Entity.find_one(eid=str(eid))
        if entity is None:
            LOGGER.exception('Error getting entity. '
                             'Entity %s does not exist.', eid)
            return {
                'message': 'Entity {} does not exist'.format(eid)
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

        @apiSuccess {Object[]} entities List of entity objects
        @apiSuccess {Object} [entities.eid] ID of the entity.
        @apiSuccess {String} [entities.property] Properties of the entity.
        """
        documents = schema.Entity.find()
        try:
            entities = [get_entity(document, features=False) for document in documents]
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 500
        else:
            print(entities)
            return {'entities': entities}


class Events(Resource):
    def get(self):
        """
        @api {get} /events/ Get the events of an entity
        @apiName GetEvents
        @apiGroup Entity
        @apiVersion 1.0.0
        @apiDescription Get the history/events of a entity.

        @apiParam {String} eid EID of the entity.

        @apiSuccess {Object[]} events List of Event Objects.
        """
        eid = request.args.get('eid', None)
        entity = schema.Entity.find_one(eid=eid)
        if entity is None:
            LOGGER.exception('Error getting entity. Entity %s does not exist.', eid)
            return {'message': 'Entity {} does not exist'.format(eid)}, 400
        events = get_events(entity)
        return events, 200


class Case(Resource):
    def get(self, case_id):
        """
        @api {get} /cases/:case_id/ Get details of a case
        @apiName GetCase
        @apiGroup Case
        @apiVersion 1.0.0
        @apiDescription Get details of a specific case.

        @apiSuccess {String} case_id ID of the case.
        @apiSuccess {String} property properties of the case
        """
        case = schema.Case.find_one(case_id=case_id)
        if case is None:
            LOGGER.exception('Error getting case. Case %s does not exist.', case_id)
            return {'message': 'Case {} does not exist'.format(case_id)}, 400

        return get_case(case), 200


class Cases(Resource):
    def get(self):
        """
        @api {get} /cases/ Get a list of cases
        @apiName GetCases
        @apiGroup Case
        @apiVersion 1.0.0
        @apiDescription Get a list of cases.

        @apiSuccess {String[]} cases List of Case ids
        """
        documents = schema.Case.find()
        try:
            case = [document.case_id for document in documents]
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 500
        else:
            return {'cases': case}, 200


class EntitiesInCase(Resource):
    def get(self, case_id):
        """
        @api {get} /entities_in_case/:case_id/ Get entities involved in a case
        @apiName GetEntitiesInCase
        @apiGroup Case
        @apiVersion 1.0.0
        @apiDescription Get entities involved in a case

        @apiSuccess {String[]} eids EIDs of entities involved in the case.
        """
        entities = schema.Entity.find(property__case_ids__contains=case_id)
        if entities is None:
            LOGGER.log('Case %s has no entities', case_id)
            return []
        return [document.eid for document in entities], 200
