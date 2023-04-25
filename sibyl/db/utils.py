import logging
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

LOGGER = logging.getLogger(__name__)


""" =====================================
BASE CLASSES
========================================"""


class ModelWrapper(ABC):
    def __init__(self, features=None):
        """
        Initialize model wrapper.
        :param features: Features the model uses, in the order it expects them
        """
        self.features = features

    @abstractmethod
    def predict(self, X):
        """
        Makes a prediction on x
        :param X: dataframe of shape (n_entities, n_features)
                  Data to predict on. Column names should be feature names
        :return: list of size (n_entities, )
                 Prediction for entities
        """
        return X


class Transformer(ABC):
    @abstractmethod
    def transform(self, X):
        """
        Transform x for a model
        :param X: DataFrame of shape (n_samples, n_features_original)
                  Input to model
        :return: DataFrame of shape (n_samples, n_features_transformed)
                 Transformed output
        """

    def transform_contributions_shap(self, contributions):
        """
        Combine contribution values, assuming the SHAP algorithm
        :param contributions: DataFrame of shape (n_samples, n_features_original)
        :return: DataFrame of shape (n_samples, n_features_transformed)
        """
        return contributions

    def transform_importances_pfi(self, importances):
        """
        Combine importance values, assuming Permutation Feature Importance algorithm
        :param importances: DataFrame of shape (n_samples, n_features_original)
        :return: DataFrame of shape (n_samples, n_features_transformed)
        """
        return importances


"""=====================================
Implementations
======================================"""


def convert_from_categorical(cat_data, mappings):
    cols = cat_data.columns
    num_rows = cat_data.shape[0]

    # List of column names that will be converted to one-hot
    cat_cols = mappings["name"].values

    data = {}
    for col in cols:
        if col not in cat_cols:
            data[col] = cat_data[col]
        if col in cat_cols:
            values = cat_data[col].astype(str)
            relevant_rows = mappings[mappings["name"] == col]
            for ind in relevant_rows.index:
                new_col_name = relevant_rows["original_name"][ind]
                data[new_col_name] = np.zeros(num_rows)
                data[new_col_name][np.where(values == relevant_rows["value"][ind])] = 1
    return pd.DataFrame(data)


def to_probs(arr):
    odds = np.exp(arr)
    return odds / (1 + odds)


def preds_to_scores(preds, thresholds):
    return np.digitize(to_probs(preds), thresholds, right=True) + 1


class ModelWrapperThresholds(ModelWrapper):
    def __init__(self, base_model, thresholds, features=None):
        """
        Initialize the model wrapper
        :param base_model: base model with which to predict.
               Should have a base_model.predict() function
        :param thresholds: thresholds to use for scoring
        :param features: Features the model uses, in the order it expects them
        """
        self.base_model = base_model
        self.thresholds = thresholds
        super().__init__(features)

    def __call__(self, x):
        return self.predict(x)

    def predict(self, x):
        """
        Predict on x, then convert to probabilities and scores based on
        thresholds
        :param x: dataframe of shape (n_entities, n_features)
                  Data to predict on. Column names should be feature names
        :return: list of size (n_entities, )
                 Prediction for entities
        """
        x = super().predict(x)
        pred = self.base_model.predict(x)
        scores = preds_to_scores(pred, self.thresholds)
        return scores


def combine_contributions_from_mappings(contributions, mappings):
    working_contributions = contributions.copy()
    agg_features = np.unique(mappings["name"].to_numpy())
    for agg_feature in agg_features:
        component_features = mappings[mappings["name"] == agg_feature]["original_name"]
        new_contribution = contributions[component_features].sum(axis=1)
        working_contributions = working_contributions.drop(component_features, axis="columns")
        working_contributions[agg_feature] = new_contribution
    return working_contributions


class MappingsTransformer(ABC):
    def __init__(self, mappings, features):
        self.mappings = mappings
        self.features = features

    def transform(self, X):
        return convert_from_categorical(X, self.mappings)[self.features]

    def transform_contributions(self, contributions):
        return combine_contributions_from_mappings(contributions, self.mappings)
