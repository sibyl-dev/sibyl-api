"""SibylApp Database Schema.

This module contains the classes that define the Orion Database Schema:
    * Entitiy
"""

import logging
from datetime import datetime

from mongoengine import CASCADE, fields
from pip._internal.operations import freeze

from sibylapp.db.base import SibylAppDocument

LOGGER = logging.getLogger(__name__)


class Event(SibylAppDocument):
    """Event object.

    A **Event** represents ...
    """
    entity = fields.ReferenceField(Entity, required=True)
    datetime = fields.DateTimeField(required=True)
    # TODO: choices from config
    type = fields.StringField(required=True)
    property = fields.DictField() # {property:value}


class Entity(SibylAppDocument):
    """Entity object.

    A **Entity** represents ...
    """

    # TODO: add y value

    eid = fields.StringField()
    # TODO: default function to assign value to counter if eid not given

    features = fields.ListField(fields.DictField()) # {feature:value}
    property = fields.DictField() # {property:value}

    outcomes = fields.ListField(fields.ReferenceField(Event))  # contains Event objects

    unique_key_fields = ['eid']


class Category(SibylAppDocument):
    name = fields.StringField(required=True)
    color = fields.StringField()


class Feature(SibylAppDocument):
    """Feature object.

    A **Feature** represents ...
    """
    name = fields.StringField(required=True)
    description = fields.StringField()
    category = fields.ReferenceField(Category)
    type = fields.StringField(choices=['boolean', 'categorical', 'numeric'])

    unique_key_fields = ['name']


class Model(SibylAppDocument):
    """Model object.

    A **Model** represents ...
    """
    model = fields.BinaryField(required=True) # the model (must have model.predict())

    name = fields.StringField()
    description = fields.StringField()
    performance = fields.StringField()
    importances = fields.DictField()  # {feature_name:importance}
    predictions = fields.DictField() # {entity_id:prediction}

    explainer = fields.BinaryField() # trained contribution explainer
    training_set = fields.ReferenceField(TrainingSet)


class TrainingSet(SibylAppDocument):
    """Dataset object.

    A **Dataset** represents ...
    """
    # TODO: should we enforce 1-to-1 mappings between datasets and models for
    #  simplicity?
    entity_ids = fields.ListField(fields.ReferenceField(Entity))
    neighbors = fields.BinaryField() # trained NN classifier



