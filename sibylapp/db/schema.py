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
    features = fields.ListField(fields.DictField())
    property = fields.DictField()

    unique_key_fields = ['eid']
