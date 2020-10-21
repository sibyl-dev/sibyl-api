import json
import os
import pickle
import random

import numpy as np
import pandas as pd
from mongoengine import connect
from pymongo import MongoClient
from sklearn.linear_model import Lasso

from pyreal.explainers import LocalFeatureContribution
from sibylapp.db import schema
from sibylapp.db.utils import MappingsTransformer, ModelWrapperThresholds


def get_rows_by_output(output, predict, X, row_labels=None):
    """
    Return the indices of the rows in X that get predicted as output

    :param output: int or array-like
           The output or outputs to look for
    :param predict: function array-like (X.shape) -> (X.shape[0])
           The prediction function
    :param X: Dataframe of shape(n_samples, n_features)
           The data to look through
    :param row_labels: None or array_like of shape (n_samples,)
           If not None, return the row_labels of relevant rows instead of
           numerical indices
    :return: array_like
            The indices or row_labels of the rows of X that result in output
            when run through predict
    """
    preds_train = predict(X)
    if np.isscalar(output):
        output = [output]
    xs_of_interest = np.isin(preds_train, output)
    if row_labels is None:
        row_labels = np.arange(0, len(xs_of_interest))
    else:
        row_labels = np.asanyarray(row_labels)
    return row_labels[xs_of_interest]


def summary_categorical(X):
    """
    Returns the unique values and counts for each column in X
    :param X: array_like of shape (n_samples, n_features)
           The data to summarize
    :return values: list of length n_features of arrays
                    The unique values for each feature
    :return count: list of length n_features
                   The number of occurrences of each unique value
                   for each feature
    """
    all_values = []
    all_counts = []
    X = np.asanyarray(X)
    for col in X.T:
        values, counts = np.unique(col, return_counts=True)
        all_values.append(values)
        all_counts.append(counts)
    return all_values, all_counts


def summary_numeric(X):
    """
    Find the minimum, 1st quartile, median, 2nd quartile, and maximum of the
    values for each column in X
    :param X: array_like of shape (n_samples, n_features)
           The data to summarize
    :return: A list of length (n_features) of lists of length 5
             The metrics for each feature:
             [minimum, 1st quartile, median, 2nd quartile, and maximum]
    """
    all_metrics = []
    X = np.asanyarray(X)
    for col in X.T:
        quartiles = np.quantile(col, [0.25, 0.5, 0.75])
        maximum = col.max()
        minimum = col.min()
        all_metrics.append([float(minimum), float(quartiles[0]), float(quartiles[1]),
                            float(quartiles[2]), float(maximum)])
    return all_metrics


def load_data(features, dataset_filepath):
    data = pd.read_csv(dataset_filepath)

    y = data.PRO_PLSM_NEXT730_DUMMY
    X = data[features]

    return X, y


def convert_to_categorical(X, mappings):
    cols = X.columns
    num_rows = X.shape[0]
    cat_cols = mappings['original_name'].values
    cat_data = {}
    for col in cols:
        if col not in cat_cols:
            cat_data[col] = X[col]
        if col in cat_cols:
            new_name = mappings[mappings['original_name'] == col]["name"].values[0]
            if new_name not in cat_data:
                cat_data[new_name] = np.empty(num_rows, dtype='object')
                # Handle a few specific cases
                if new_name == "PRI_FOCUS_GENDER":
                    cat_data[new_name] = np.full(num_rows, "Male", dtype='object')
                if new_name == "PRI_VICTIM_COUNT":
                    cat_data[new_name] = np.full(num_rows, "0")
            cat_data[new_name][np.where(X[col] == 1)] = \
                mappings[mappings['original_name'] == col]["value"].values[0]
    return pd.DataFrame(cat_data)


def insert_features(filepath):
    features_df = pd.read_csv(filepath)

    references = [schema.Category.find_one(name=cat) for cat in features_df['category']]
    features_df = features_df.drop('category', axis='columns')
    features_df['category'] = references

    items = features_df.to_dict(orient='records')
    schema.Feature.insert_many(items)
    return features_df["name"]


def insert_categories(filepath):
    cat_df = pd.read_csv(filepath)
    items = cat_df.to_dict(orient='records')
    schema.Category.insert_many(items)


def load_model_from_weights_sklearn(weights_filepath, model_base):
    """
    Load the model
    :return: (model, model features)
    """
    model_weights = pd.read_csv(weights_filepath)

    model = model_base
    dummy_X = np.zeros((1, model_weights.shape[1] - 1))
    dummy_y = np.zeros(model_weights.shape[1] - 1)
    model.fit(dummy_X, dummy_y)

    model.coef_ = np.array(model_weights["weight"][1:])
    model.intercept_ = model_weights["weight"][0]
    return model, model_weights["name"][1:]


def load_mappings_transformer(mappings_filepath, features):
    mappings = pd.read_csv(mappings_filepath)
    mappings = mappings[mappings["include"]]
    return MappingsTransformer(mappings, features)


def insert_model(features, model_filepath, dataset_filepath,
                 importance_filepath=None, explainer_filepath=None):
    thresholds = [0.01174609, 0.01857239, 0.0241622, 0.0293587,
                  0.03448975, 0.0396932, 0.04531139, 0.051446,
                  0.05834176, 0.06616039, 0.07549515, 0.08624243,
                  0.09912388, 0.11433409, 0.13370343, 0.15944484,
                  0.19579651, 0.25432879, 0.36464856, 1.0]
    base_model, model_features = load_model_from_weights_sklearn(
        model_filepath, Lasso())

    model = ModelWrapperThresholds(base_model, thresholds, features=model_features)
    transformer = load_mappings_transformer(os.path.join(directory, "mappings.csv"),
                                            model_features)

    dataset, targets = load_data(features, dataset_filepath)

    model_serial = pickle.dumps(model)
    transformer_serial = pickle.dumps(transformer)

    texts = {
        "name": "Lasso Regression Model",
        "description": "placeholder",
        "performance": "placeholder"
    }
    name = texts["name"]
    description = texts["description"]
    performance = texts["performance"]

    if importance_filepath is not None:
        importance_df = pd.read_csv(importance_filepath)
        importance_df = importance_df.set_index("name")
    else:
        raise NotImplementedError()

    importances = importance_df.to_dict(orient='dict')["importance"]

    if explainer_filepath is not None:
        print("Loading explainer from file")
        with open(explainer_filepath, "rb") as f:
            explainer_serial = f.read()
    else:
        explainer = LocalFeatureContribution(base_model, dataset.sample(100),
                                             contribution_transformers=transformer,
                                             e_algorithm="shap",
                                             e_transforms=transformer,
                                             m_transforms=transformer)
        explainer_serial = pickle.dumps(explainer)

    items = {
        "model": model_serial,
        "transformer": transformer_serial,
        "name": name,
        "description": description,
        "performance": performance,
        "importances": importances,
        "explainer": explainer_serial,
        "training_set": set_doc
    }
    schema.Model.insert(**items)


def insert_entities(values_filepath, features_names, mappings_filepath=None,
                    counter_start=0, num=0, include_referrals=False):
    values_df = pd.read_csv(values_filepath)[features_names + ["eid"]]
    if mappings_filepath is not None:
        mappings = pd.read_csv(mappings_filepath)
        mappings = mappings[mappings["include"]]
        values_df = convert_to_categorical(values_df, mappings)
    if num > 0:
        values_df = values_df.iloc[counter_start:num + counter_start]
    eids = values_df["eid"]

    referrals = schema.Referral.find()

    raw_entities = values_df.to_dict(orient="records")
    entities = []
    for raw_entity in raw_entities:
        entity = {}
        entity["eid"] = str(raw_entity["eid"])
        del raw_entity["eid"]
        entity["features"] = raw_entity
        if include_referrals:
            entity["property"] = {"referral_ids": [random.choice(referrals).referral_id]}
        entities.append(entity)
    schema.Entity.insert_many(entities)
    return eids


def insert_training_set(eids):
    references = [schema.Entity.find_one(eid=str(eid)) for eid in eids]
    training_set = {"entities": references}

    set_doc = schema.TrainingSet.insert(**training_set)
    return set_doc


def insert_referrals(filepath):
    referral_df = pd.read_csv(filepath)
    items_raw = referral_df.to_dict(orient='records')
    items = []
    for item_raw in items_raw:
        item = {"referral_id": str(item_raw["referral_id"]),
                "property": {"team": item_raw["team"]}}
        items.append(item)
    schema.Referral.insert_many(items)


def generate_feature_distribution_doc(save_path, model, transformer,
                                      dataset_filepath, features_filepath):
    features = pd.read_csv(features_filepath)
    feature_names = features["name"].append(pd.Series(["PRO_PLSM_NEXT365_DUMMY",
                                                       "PRO_PLSM_NEXT730_DUMMY"]))
    dataset, targets = load_data(feature_names, dataset_filepath)

    boolean_features = features[features['type'].isin(['binary', 'categorical'])]["name"]
    boolean_features = boolean_features.append(pd.Series(["PRO_PLSM_NEXT365_DUMMY",
                                                          "PRO_PLSM_NEXT730_DUMMY"]))
    dataset_cat = dataset[boolean_features]

    numeric_features = features[features['type'] == 'numeric']["name"]
    dataset_num = dataset[numeric_features]

    summary_dict = {}
    for output in range(1, 21):
        row_details = {}
        rows = get_rows_by_output(output, model.predict, dataset, row_labels=None)

        count_total = len(rows)
        count_removed = sum(targets.iloc[rows])
        row_details["total cases"] = count_total
        row_details["total removed"] = count_removed

        cat_summary = summary_categorical(dataset_cat.iloc[rows].applymap(str))
        num_summary = summary_numeric(dataset_num.iloc[rows])

        distributions = {}
        for (i, name) in enumerate(boolean_features):
            distributions[name] = {"type": "categorical", "metrics": [cat_summary[0][i].tolist(),
                                                                      cat_summary[1][i].tolist()]}
        for (i, name) in enumerate(numeric_features):
            distributions[name] = {"type": "numeric", "metrics": num_summary[i]}
        row_details["distributions"] = distributions

        summary_dict[output] = row_details

    with open(save_path, 'w') as f:
        json.dump(summary_dict, f, indent=4, sort_keys=True)


def test_validation():
    pass


if __name__ == "__main__":
    # CONFIGURATIONS
    include_database = False
    client = MongoClient("localhost", 27017)
    connect('sibyl', host='localhost', port=27017)
    directory = os.path.join("..", "..", "..", "sibyl-data")

    # INSERT CATEGORIES
    insert_categories(os.path.join(directory, "categories.csv"))

    # INSERT FEATURES
    feature_names = insert_features(os.path.join(directory, "features.csv")).tolist()

    # INSERT REFERRALS
    insert_referrals(os.path.join(directory, "referrals.csv"))

    # INSERT ENTITIES
    eids = insert_entities(os.path.join(directory, "true_entities.csv"), feature_names,
                           mappings_filepath=os.path.join(directory, "mappings.csv"),
                           include_referrals=True)

    # INSERT FULL DATASET
    if include_database:
        eids = insert_entities(os.path.join(directory, "dataset.csv"), feature_names,
                               counter_start=17, num=100000)
    set_doc = insert_training_set(eids)

    # INSERT MODEL
    model_filepath = os.path.join(directory, "weights.csv")
    dataset_filepath = os.path.join(directory, "dataset.csv")
    importance_filepath = os.path.join(directory, "importances.csv")

    insert_model(features=feature_names, model_filepath=model_filepath,
                 dataset_filepath=dataset_filepath, importance_filepath=importance_filepath)

    # PRE-COMPUTE DISTRIBUTION INFORMATION
    #generate_feature_distribution_doc("precomputed/agg_distributions.json", model, transformer,
    #                                  os.path.join(directory, "agg_dataset.csv"),
    #                                  os.path.join(directory, "agg_features.csv"))
    test_validation()
