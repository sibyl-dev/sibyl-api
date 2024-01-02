"""MTV DB Explorer model.

This model defines the ``mtv.db.explorer.DBExplorer``, which provides
a simple programatic access to creating and reading objects in the MTV Database.
"""

import json
import logging

from gridfs import GridFS
from mongoengine import connect
from pymongo.database import Database

from sibyl.db import schema

LOGGER = logging.getLogger(__name__)


class DBExplorer:
    """User interface for the Orion Database.

    This class provides a user-frienly programming interface to
    interact with the Orion database models.

    Args:
        user (str):
            Unique identifier of the user that creates this OrionExporer
            instance. This username or user ID will be used to populate
            the ``created_by`` field of all the objects created in the
            database during this session.
        database (str):
            Name of the MongoDB database to use. Defaults to ``orion``.
        mongodb_config (dict or str):
            A dict or a path to JSON file with additional arguments can be
            passed to provide connection details different than the defaults
            for the MongoDB Database:
                * ``host``: Hostname or IP address of the MongoDB Instance.
                * ``port``: Port to which MongoDB is listening.
                * ``username``: username to authenticate with.
                * ``password``: password to authenticate with.
                * ``authentication_source``: database to authenticate against.

    Examples:
        Simples use case:
        >>> orex = OrionExplorer('my_username')

        Passing a path to a JSON file with connection details.
        >>> orex = OrionExplorer(
        ...      user='my_username',
        ...      database='orion',
        ...      mongodb_config='/path/to/my/mongodb_config.json',
        ... )

        Passing all the possible initialization arguments as a dict:
        >>> mongodb_config = {
        ...      'host': 'localhost',
        ...      'port': 27017,
        ...      'username': 'orion',
        ...      'password': 'secret_password',
        ...      'authentication_source': 'admin',
        ... }
        >>> orex = OrionExplorer(
        ...      user='my_username',
        ...      database='orion',
        ...      mongodb_config=mongodb_config
        ... )
    """

    def __init__(self, user, database="orion", mongodb_config=None):
        """Initiaize this OrionDBExplorer.

        Args:
            user (str):
                Unique identifier of the user that creates this OrionExporer
                instance. This username or user ID will be used to populate
                the ``created_by`` field of all the objects created in the
                database during this session.
            database (str):
                Name of the MongoDB database to use. Defaults to ``orion``.
            mongodb_config (dict or str):
                A dict or a path to JSON file with additional arguments can be
                passed to provide connection details different than the defaults
                for the MongoDB Database:
                    * ``host``: Hostname or IP address of the MongoDB Instance.
                    * ``port``: Port to which MongoDB is listening.
                    * ``username``: username to authenticate with.
                    * ``password``: password to authenticate with.
                    * ``authentication_source``: database to authenticate against.
        """
        if mongodb_config is None:
            mongodb_config = dict()
        elif isinstance(mongodb_config, str):
            with open(mongodb_config) as config_file:
                mongodb_config = json.load(config_file)
        elif isinstance(mongodb_config, dict):
            mongodb_config = mongodb_config.copy()

        self.user = user
        self.database = mongodb_config.pop("database", database)
        self._db = connect(database, **mongodb_config)
        self._fs = GridFS(Database(self._db, self.database))

    def drop_database(self):
        """Drop the database.

        This method is used for development purposes and will
        most likely be removed in the future.
        """
        self._db.drop_database(self.database)

    # ####### #
    # Dataset #
    # ####### #

    def add_dataset(self, name, entity=None):
        """Add a new Dataset object to the database.

        The Dataset needs to be given a name and, optionally, an identitifier,
        name or ID, of the entity which produced the Dataset.

        Args:
            name (str):
                Name of the Dataset
            entity (str):
                Name or Id of the entity which this Dataset is associated to.
                Defaults to ``None``.

        Raises:
            NotUniqueError:
                If a Dataset with the same name and entity values already exists.

        Returns:
            Dataset
        """
        return schema.Dataset.insert(name=name, entity=entity, created_by=self.user)

    def get_datasets(self, name=None, entity=None, created_by=None):
        """Query the Datasets collection.

        All the details about the matching Datasets will be returned in
        a ``pandas.DataFrame``.

        All the arguments are optional, so a call without arguments will
        return a table with information about all the Datasets availabe.

        Args:
            name (str):
                Name of the Dataset.
            entity (str):
                Name or Id of the entity which returned Datasets need to be
                associated to.
            created_by (str):
                Unique identifier of the user that created the Datasets.

        Returns:
            pandas.DataFrame
        """
        return schema.Dataset.find(as_df_=True, name=name, entity=entity, created_by=created_by)

    def get_dataset(self, dataset=None, name=None, entity=None, created_by=None):
        """Get a Dataset object from the database.

        All the arguments are optional but empty queries are not allowed, so at
        least one argument needs to be passed with a value different than ``None``.

        Args:
            dataset (Dataset, ObjectID or str):
                Dataset object (or the corresponding ObjectID, or its string
                representation) that we want to retreive.
            name (str):
                Name of the Dataset.
            entity (str):
                Name or Id of the entity which this Dataset is associated to.
            created_by (str):
                Unique identifier of the user that created the Dataset.

        Raises:
            ValueError:
                If the no arguments are passed with a value different than
                ``None`` or the query resolves to more than one object.

        Returns:
            Dataset
        """
        return schema.Dataset.get(dataset=dataset, name=name, entity=entity, created_by=created_by)
