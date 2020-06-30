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


class Entity(SibylAppDocument):
    """Entity object.

    A **Entity** represents ...
    """
    eid = fields.StringField(required=True)

    features = fields.ListField(fields.DictField()) # {feature:value}
    property = fields.DictField() # {property:value}

    unique_key_fields = ['eid']


class Feature(SibylAppDocument):
    """Feature object.

    A **Feature** represents ...
    """
    name = fields.StringField(required=True)
    description = fields.StringField()
    category = fields.StringField()  # TODO: should categories have IDs?
    type = fields.StringField(choices=['boolean','categorical','numeric'])
    outcomes = fields.ListField() # contains Event objects

    unique_key_fields = ['name']


class Model(SibylAppDocument):
    """Model object.

    A **Model** represents ...
    """
    mid = fields.StringField(required=True)
    predict = fields.BinaryField(required=True) # the prediction function
        # TODO: is this the best way to do this?

    name = fields.StringField()
    description = fields.StringField()
    performance = fields.StringField()
    importances = fields.DictField()  # {feature_name:importance}
    predictions = fields.DictField() # {entity_id:prediction}

    explainer = fields.BinaryField() # trained contribution explainer

    unique_key_fields = ['id']


class Dataset(SibylAppDocument):
    """Dataset object.

    A **Dataset** represents ...
    """
    # TODO: should we enforce 1-to-1 mappings between datasets and models for
    #  simplicity?
    mid = fields.StringField(required=True)
    data_X = fields.DictField(required=True) # {feature:[values]}
    data_y = fields.ListField(required=True) # [values]

    neighbors = fields.BinaryField() # trained NN classifier

    unique_key_fields = ['mid']


class Event(SibylAppDocument):
    """Event object.

    A **Event** represents ...
    """
    date = fields.DateField(required=True)
    # TODO: choices from config
    type = fields.StringField(required=True)
    property = fields.DictField() # {property:value}


class FeatureContributions(SibylAppDocument):
    """FeatureContributions object.

       A **FeatureContributions** represents ...
    """
    eid = fields.StringField(required=True)
    mid = fields.StringField(required=True)

    scores = fields.DictField(required=True) # {feature:contribution}


class FeatureDistributions(SibylAppDocument):
    """FeatureDistributions object.

    A **FeatureDistributions** represents ...
    """
    mid = fields.StringField(required=True)
    prediction = fields.BinaryField(required=True)
    distributions = fields.DictField() # {feature:[type, ...]}
    #   type can be numeric or categorical.
    #          If numeric, ... -> min, 1st quart, median, 3rd quart, max
    #          If categorical, ... -> [[values],[counts]]




