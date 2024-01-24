"""Sibyl Database Schema.

This module contains the classes that define the Sibyl Database Schema
"""

import logging

import pandas as pd
from mongoengine import DENY, NULLIFY, PULL, Document, ValidationError, fields

from sibyl.db.base import SibylDocument

LOGGER = logging.getLogger(__name__)


def _valid_id(val):
    if val is not None and not isinstance(val, str):
        raise ValidationError("IDs must be type string, given %s" % val)


def _valid_row_ids(val):
    if isinstance(val, str):
        raise ValidationError("row_ids must be list of strings")
    try:
        for row_id in val:
            if not isinstance(row_id, str):
                raise ValidationError("all row_ids must be type string, given %s" % row_id)
    except TypeError:
        raise ValidationError("val must be a list of valid row_ids")
    if len(val) != len(set(val)):
        raise ValidationError("all row_ids for a given eid must be unique")


def _eid_exists(val):
    if Entity.find_one(eid=val) is None:
        raise ValidationError("eid provided (%s) does not exist" % val)


def _validate_training_set(entities):
    for entity in entities:
        if entity.labels is None or entity.labels.keys() != entity.features.keys():
            raise ValidationError(
                "All training set entries must have one label per row. Incorrect labels on eid {}"
                .format(entity.eid)
            )


class Event(SibylDocument):
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

    unique_key_fields = ["event_id"]


class Entity(SibylDocument):
    """
    An **Entity** holds the feature values and details for one model input

    Attributes
    ----------
    eid : str
        Unique ID of the entity
    row_ids : list [str]
    features : dict {feature_name : feature_value}
        Feature values for the entity
    property : dict {property : value}
        Domain-specific properties
    labels : dict {row_id : label}
    events : list [Event object]
        List of events this entity was involved in
    """

    eid = fields.StringField(validation=_valid_id, unique=True, required=True)
    row_ids = fields.ListField(validation=_valid_row_ids, required=True)

    features = fields.DictField(required=True)  # {row_id: {feature:value}}
    property = fields.DictField()  # {property:value}
    labels = fields.DictField()  # {row_id: ground_truth_label}, as provided

    events = fields.ListField(fields.ReferenceField(Event, reverse_delete_rule=PULL))


class Category(SibylDocument):
    """
    A **Category** holds information about a feature category

    Attributes
    ----------
    name : str
        Name of the category
    color : str
        Hexidecimal color that should be used for the category
    abbreviation : str
        Two- or three-character abbreviation of the category
    """

    name = fields.StringField(required=True)
    color = fields.StringField()
    abbreviation = fields.StringField(max_length=3)

    unique_key_fields = ["name", "abbreviation"]


class Feature(SibylDocument):
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
    values: list [str]
        Possible values for categorical features
    """

    name = fields.StringField(required=True)
    description = fields.StringField()
    negated_description = fields.StringField()
    category = fields.StringField()  # name of Category
    type = fields.StringField(choices=["boolean", "categorical", "numeric"], required=True)
    values = fields.ListField(fields.StringField())

    def clean(self):
        if self.type != "categorical" and self.values:
            raise ValidationError("Values should only be provided for categorical features")

    unique_key_fields = ["name"]


class TrainingSet(SibylDocument):
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
        fields.ReferenceField(Entity, reverse_delete_rule=PULL), validation=_validate_training_set
    )
    neighbors = fields.BinaryField()  # trained NN classifier

    def to_dataframe(self):
        """
        Returns this dataset as a Pandas dataframe
        :return: dataframe
        """
        features = [
            dict(entity.features[row_id], **{"y": entity.labels[row_id]})
            for entity in self.entities
            for row_id in entity.features
        ]
        training_set_df = pd.DataFrame(features)
        return training_set_df


class Model(SibylDocument):
    """
    A **Model** holds information about a model

    Attributes
    ----------
    model_id : str
        Unique ID (name) of the model
    description : str
        Description of the model
    performance : str
        Description of performance
    importances : dict {feature_name : importance}
        Importances of all features to the model
    realapp : explanation application object
        Trained contribution explainer
    training_set : TrainingSet
        Training set for the model
    """

    model_id = fields.StringField(required=True, unique=True)
    description = fields.StringField()
    performance = fields.StringField()
    importances = fields.DictField()  # {feature_name:importance}

    realapp = fields.BinaryField(required=True)
    training_set = fields.ReferenceField(TrainingSet, reverse_delete_rule=DENY)


class EntityGroup(SibylDocument):
    """
    An **EntityGroup** contains information about some categorization for entities
    Attributes
    ----------
    group_id : str
        ID of the group
    property : dict {property : value}
        Domain specific properties
    """

    group_id = fields.StringField(required=True, validation=_valid_id)
    property = fields.DictField()


class Context(SibylDocument):
    """
    A **Context** contains information about UI configuration options specific to the given
    context.
    Attributes
    context_id: str
        ID of the context
    configs : dict {key : value}
        dictionary of application-specific configurations
    """

    context_id = fields.StringField(required=True, validation=_valid_id)
    config = fields.DictField()
