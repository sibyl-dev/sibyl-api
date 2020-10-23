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


def get_referral(referral_doc):
    referral = {
        'referral_id': referral_doc.referral_id,
        'property': referral_doc.property
    }
    return referral


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
        @apiSuccess {String[]} [property.referral_ids] IDs of referrals the entity
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
                    "referral_ids": ["ca19", "ca88", "ca133"]
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


class Referral(Resource):
    def get(self, referral_id):
        """
        @api {get} /referrals/:referral_id/ Get details of a referral
        @apiName GetReferral
        @apiGroup referral
        @apiVersion 1.0.0
        @apiDescription Get details of a specific referral.

        @apiSuccess {String} referral_id ID of the referral.
        @apiSuccess {String} property properties of the referral
        """
        referral = schema.Referral.find_one(referral_id=referral_id)
        if referral is None:
            LOGGER.exception('Error getting referral. referral %s does not exist.', referral_id)
            return {'message': 'referral {} does not exist'.format(referral_id)}, 400

        return get_referral(referral), 200


class Referrals(Resource):
    def get(self):
        """
        @api {get} /referrals/ Get a list of referrals
        @apiName GetReferrals
        @apiGroup referral
        @apiVersion 1.0.0
        @apiDescription Get a list of referrals.

        @apiSuccess {String[]} referrals List of referral ids
        """
        documents = schema.Referral.find()
        try:
            referral = [document.referral_id for document in documents]
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 500
        else:
            return {'referrals': referral}, 200


class EntitiesInReferral(Resource):
    def get(self, referral_id):
        """
        @api {get} /entities_in_referral/:referral_id/ Get entities involved in a referral
        @apiName GetEntitiesInReferral
        @apiGroup referral
        @apiVersion 1.0.0
        @apiDescription Get entities involved in a referral

        @apiSuccess {String[]} eids EIDs of entities involved in the referral.
        """
        entities = schema.Entity.find(property__referral_ids__contains=referral_id)
        if entities is None:
            LOGGER.log(20, 'referral %s has no entities' % str(referral_id))
            return []
        return [document.eid for document in entities], 200
