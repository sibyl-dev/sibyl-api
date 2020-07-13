import logging
import pickle
from calendar import monthrange
from datetime import datetime, timezone

import numpy as np
from pymongo import MongoClient

from sibylapp.db import schema

LOGGER = logging.getLogger(__name__)


def to_probs(arr):
    odds = np.exp(arr)
    return odds / (1 + odds)


def preds_to_scores(preds, thresholds):
    return np.digitize(to_probs(preds), thresholds, right=True)+1


class ModelWrapper:
    def __init__(self, base_model, features=None):
        self.base_model = base_model
        self.features = features
        self.thresholds = [0.01174609, 0.01857239, 0.0241622, 0.0293587,
                           0.03448975, 0.0396932, 0.04531139, 0.051446,
                           0.05834176, 0.06616039, 0.07549515, 0.08624243,
                           0.09912388, 0.11433409, 0.13370343, 0.15944484,
                           0.19579651, 0.25432879, 0.36464856, 1.0]

    def predict(self, x):
        """
        Expects x in the form of dataframe?{feature_name:value, ...}
        Returns a single value
        """
        if self.features is not None:
            x = x[self.features]

        pred = self.base_model.predict(x)
        scores = preds_to_scores(pred, self.thresholds).tolist()
        return scores


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
