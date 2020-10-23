"""SibylApp Database Schema.

This module contains the classes that define the SibylApp Database Schema:
    * Event
    * Entitiy
    * Category
    * Feature
    * TrainingSet
    * Model
    * Case
"""

import logging

import pandas as pd
from mongoengine import DENY, NULLIFY, PULL, ValidationError, fields

from sibylapp.db.base import SibylAppDocument

LOGGER = logging.getLogger(__name__)


def _valid_id(val):
    if val is not None and not isinstance(val, str):
        raise ValidationError("eid must be type string, given %s" % val)


def _eid_exists(val):
    if Entity.find_one(eid=val) is None:
        raise ValidationError("eid provided (%s) does not exist" % val)


class Event(SibylAppDocument):
    """
    An **Event** holds information about an event an entity was involved with

    Attributes
    ----------
    event_id : str
        Reference ID for the event
    datetime : DateTime
        Date and time of the event
    type : str
        Type of event
    property : dict {property : value}
        Domain specific properties of the event
    """
    event_id = fields.StringField()
    datetime = fields.DateTimeField(required=True)
    # TODO: choices from config
    type = fields.StringField(required=True)
    property = fields.DictField()  # {property:value}

    unique_key_fields = ['event_id']


class Entity(SibylAppDocument):
    """
    An **Entity** holds the feature values and details for one model input

    Attributes
    ----------
    eid : str
        Unique ID of the entity
    features : dict {feature_name : feature_value}
        Feature values for the entity
    property : dict {property : value}
        Domain-specific properties
    events : list [Event object]
        List of events this entity was involved in
    """
    eid = fields.StringField(validation=_valid_id)

    features = fields.DictField()  # {feature:value}
    property = fields.DictField()  # {property:value}

    events = fields.ListField(
        fields.ReferenceField(Event, reverse_delete_rule=PULL))

    unique_key_fields = ['eid']


class Category(SibylAppDocument):
    """
    A **Category** holds information about a feature category

    Attributes
    ----------
    name : str
        Name of the category
    color : str
        Hexidecimal color that should be used for the category
    abbreviation : str
        Two or three character abbreviation of the category
    """
    name = fields.StringField(required=True)
    color = fields.StringField()
    abbreviation = fields.StringField(max_length=3)

    unique_key_fields = ['name', 'abbreviation']


class Feature(SibylAppDocument):
    """
    A **Feature** hold information about a model input feature

    Attributes
    ----------
    name : str
        Name of the feature
    description : str
        Readable description of the feature
    negated_description : str
        Readable description of the feature in negated form
    category : Category object
        Category the feature belongs to
    type : str
        Feature type (one of binary, categorical, and numeric)
    """
    name = fields.StringField(required=True)
    description = fields.StringField()
    negated_description = fields.StringField()
    category = fields.ReferenceField(Category, reverse_delete_rule=NULLIFY)
    type = fields.StringField(choices=['binary', 'categorical', 'numeric'])

    unique_key_fields = ['name']


class TrainingSet(SibylAppDocument):
    """
    A **TrainingSet** is a set of entities that can be used to explain a given model

    Attributes
    ----------
    entities : list [Entity object[
        List of entities in the dataset
    neighbors : trained NN classifier
        Trained nearest neighbors classifier for the dataset
    """
    entities = fields.ListField(
        fields.ReferenceField(Entity, reverse_delete_rule=PULL))
    neighbors = fields.BinaryField()  # trained NN classifier

    def to_dataframe(self):
        """
        Returns this dataset as a Pandas dataframe
        :return: dataframe
        """
        features = [entity.features for entity in self.entities]
        training_set_df = pd.DataFrame(features)
        return training_set_df


class Model(SibylAppDocument):
    """
    A **Model** holds information about a model

    Attributes
    ----------
    model : pickle-saved model
        The model object. Must have a model.predict() function
    name : str
        Name of the model
    description : str
        Description of the model
    performance : str
        Description of performance
    importances : dict {feature_name : importance}
        Importances of all features to the model
    explainer : contribution explainer
        Trained contribution explainer
    training_set : TrainingSet
        Training set for the model
    """
    model = fields.BinaryField(required=True)  # the model (must have model.predict())
    transformer = fields.BinaryField()  # the model's transformer

    name = fields.StringField()
    description = fields.StringField()
    performance = fields.StringField()
    importances = fields.DictField()  # {feature_name:importance}

    explainer = fields.BinaryField()  # trained contribution explainer
    training_set = fields.ReferenceField(TrainingSet, reverse_delete_rule=DENY)


class Referral(SibylAppDocument):
    """
    A **Case** contains information about a referral
    Attributes
    ----------
    referral_id : str
        ID of the referral
    property : dict {property : value}
        Domain specific properties
    """
    referral_id = fields.StringField(required=True, validation=_valid_id)
    property = fields.DictField()
