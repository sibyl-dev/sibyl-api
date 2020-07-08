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
    eid = fields.StringField()
    datetime = fields.DateTimeField(required=True)
    # TODO: choices from config
    type = fields.StringField(required=True)
    property = fields.DictField()  # {property:value}

    # TODO: verify eid is in Entity collection


class Entity(SibylAppDocument):
    """Entity object.

    A **Entity** represents ...
    """
    eid = fields.StringField()

    features = fields.ListField(fields.DictField())  # {feature:value}
    property = fields.DictField()  # {property:value}

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


class TrainingSet(SibylAppDocument):
    """Dataset object.

    A **Dataset** represents ...
    """
    entity_ids = fields.ListField(fields.ReferenceField(Entity))
    neighbors = fields.BinaryField()  # trained NN classifier


class Model(SibylAppDocument):
    """Model object.

    A **Model** represents ...
    """
    model = fields.BinaryField(required=True)  # the model (must have model.predict())

    name = fields.StringField()
    description = fields.StringField()
    performance = fields.StringField()
    importances = fields.DictField()  # {feature_name:importance}

    explainer = fields.BinaryField()  # trained contribution explainer
    training_set = fields.ReferenceField(TrainingSet)
