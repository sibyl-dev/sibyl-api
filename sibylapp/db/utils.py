import logging
import pickle
from calendar import monthrange
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from pymongo import MongoClient

from sibyl.db import schema

LOGGER = logging.getLogger(__name__)


def merge_databases():
    pass


def delete_datasets():
    cli = MongoClient('localhost', port=27017)
    db = cli['mtv']
    pass


def prune_dataruns():
    cli = MongoClient('localhost', port=27017)
    pass


def main():
    pass
