"""Sibyl Database Schema.

This module contains the classes that define the Sibyl Database Schema
"""

import logging

import pandas as pd
from mongoengine import DENY, NULLIFY, PULL, ValidationError, fields

from sibyl.db.base import SibylDocument

LOGGER = logging.getLogger(__name__)


def _valid_id(val):
    if val is not None and not isinstance(val, str):
        raise ValidationError("eid must be type string, given %s" % val)


def _eid_exists(val):
    if Entity.find_one(eid=val) is None:
        raise ValidationError("eid provided (%s) does not exist" % val)


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


class EntityRow(SibylDocument):
    """
    An **EntityRow** holds the feature values and details for one model input

    Attributes
    ----------
    eid : str
        Entity this row belongs to
    row_id : str
        ID of this row
    features : dict {feature_name : feature_value}
        Feature values for the entity
    label : str
        Ground-truth label for this row
    property : dict {property : value}
        Domain-specific properties
    """

    eid = fields.StringField(validation=_valid_id)
    row_id = fields.StringField(validation=_valid_id, unique_with="eid")

    features = fields.DictField()  # {feature:value}
    label = fields.StringField()

    property = fields.DictField()


class Entity(SibylDocument):
    """
    An **Entity** holds properties and EntityRows for one entity in the dataset

    Attributes
    ----------
    eid : str
        Unique ID of the entity
    rows: list [EntityRow object]
        Data rows (feature values/labels) for this entity
    groups: list [EntityGroup object]
        EntityGroups this entity belongs to
    property : dict {property : value}
        Domain-specific properties
    events : list [Event object]
        List of events this entity was involved in
    """

    eid = fields.StringField(validation=_valid_id)
    rows = fields.ListField(fields.ReferenceField(EntityRow, reverse_delete_rule=PULL))

    property = fields.DictField()  # {property:value}

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
    """

    name = fields.StringField(required=True)
    description = fields.StringField()
    negated_description = fields.StringField()
    category = fields.ReferenceField(Category, reverse_delete_rule=NULLIFY)
    type = fields.StringField(choices=["binary", "categorical", "numeric"])

    unique_key_fields = ["name"]


class TrainingSet(SibylDocument):
    """
    A **TrainingSet** is a set of entities that can be used to explain a given model

    Attributes
    ----------
    entities : list [Entity object]
        List of entities in the dataset
    neighbors : trained NN classifier
        Trained nearest neighbors classifier for the dataset
    """

    entities = fields.ListField(fields.ReferenceField(Entity, reverse_delete_rule=PULL))
    target = fields.StringField()
    neighbors = fields.BinaryField()  # trained NN classifier

    def to_dataframe(self):
        """
        Returns this dataset as a Pandas dataframe
        :return: dataframe
        """
        features = [entity.features for entity in self.entities]
        labels = [entity.label for entity in self.entities]
        training_set_df = pd.DataFrame(features)
        training_set_df["y"] = labels
        return training_set_df


class Model(SibylDocument):
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

    name = fields.StringField()
    description = fields.StringField()
    performance = fields.StringField()
    importances = fields.DictField()  # {feature_name:importance}

    explainer = fields.BinaryField()  # trained contribution explainer
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
    ----------
    terms : dict {key : term}
        dictionary of application-specific terms to use
    gui_config : dict {key : value}
        dictionary of application-specific GUI configurations
    gui_preset : string
        name of gui_preset to use, which may be used by front-end code to fill in missing
        gui_config values
    """

    terms = fields.DictField()
    gui_config = fields.DictField()
    gui_preset = fields.StringField()
