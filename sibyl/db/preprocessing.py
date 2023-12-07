import os
import pickle
import sys

import numpy as np
import pandas as pd
import yaml
from mongoengine import connect
from pymongo import MongoClient
from tqdm import tqdm

from sibyl.db import schema
from sibyl.utils import get_project_root


def _load_data(training_entity_filepath, target):
    try:
        data = pd.read_csv(training_entity_filepath)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Dataset file {training_entity_filepath} not found. Must provide valid file."
        )

    y = data[target]
    X = data.drop(target, axis="columns")

    return X, y


def _validate_model_and_explainer(explainer, train_dataset):
    """
    Run predict and explain processes to make sure everything is working correctly
    """
    explainer.predict(train_dataset.iloc[0:2])
    explainer.produce_feature_contributions(train_dataset.iloc[0:2])


def insert_features_from_csv(filepath=None):
    """
    Insert features from a csv file into the database.
    Required columns:
        - name: the name of the feature, as in the entity columns
        - type: the type of the feature, one of "numeric", "categorical", "text", "boolean"
    Optional columns:
        - description: a description of the feature
        - negated_description: a description of the feature when it is negated
        - category: the category of the feature, as in the category table

    Args:
        filepath (string): Filepath of csv file

    Returns:
        list: List of feature names inserted
    """
    try:
        features_df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Features file {filepath} not found. Must provide valid features file"
        )
    return insert_features_from_dataframe(features_df)


def insert_features_from_dataframe(features_df=None):
    """
    Insert features from a pandas dataframe into the database.
    Required columns:
        - name: the name of the feature, as in the entity columns
        - type: the type of the feature, one of "numeric", "categorical", "text", "boolean"
    Optional columns:
        - description: a description of the feature
        - negated_description: a description of the feature when it is negated
        - category: the category of the feature, as in the category table

    Args:
        features_df (DataFrame): Dataframe of feature information

    Returns:
        list: List of feature names inserted
    """
    if "category" in features_df:
        categories = set(features_df["category"])
        already_inserted_categories = schema.Category.find(as_df_=True, only_=["name"])
        if not already_inserted_categories.empty:
            already_inserted_categories = set(already_inserted_categories["name"])
        schema.Category.insert_many(
            [{"name": cat} for cat in categories if cat not in already_inserted_categories]
        )
    items = features_df.to_dict(orient="records")
    schema.Feature.insert_many(items)
    return features_df["name"].tolist()


def insert_categories_from_csv(filepath):
    """
    Insert categories from a csv file into the database.
    Required columns:
        - name: the name of the category
    Optional columns:
        - color: the color of the category (name, hex, or rgb)
        - abbreviation: the abbreviation of the category

    Args:
        filepath (string): Filepath of csv file

    Returns
        list: List of category names inserted
    """
    if filepath is None:
        return
    try:
        category_df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"Categories file {filepath} not found. ")
    return insert_features_from_dataframe(category_df)


def insert_categories_from_dataframe(category_df=None):
    """
    Insert categories from a pandas dataframe into the database.
    Required columns:
        - name: the name of the category
    Optional columns:
        - color: the color of the category (name, hex, or rgb)
        - abbreviation: the abbreviation of the category

    Args:
        category_df (DataFrame): Dataframe of category information

    Returns
        list: List of category names inserted
    """
    items = category_df.to_dict(orient="records")
    schema.Category.insert_many(items)
    return category_df["name"].tolist()


def insert_context_from_yaml(filepath):
    """
    Insert context from a yaml file into the database.
    See sibyl/templates/context_config_template.yml for an example of the format.

    Args:
        filepath (string): Filepath of yaml file containing context information
    """
    if filepath is None:
        return
    try:
        context_dict = yaml.safe_load(open(filepath, "r"))
    except FileNotFoundError:
        raise FileNotFoundError(f"Context config file {filepath} not found. ")

    return insert_context_from_dict(context_dict)


def insert_context_from_dict(context_dict):
    """
    Insert context from a python dictionary into the database.
    See sibyl/templates/context_config_template.yml for an example of config options.

    Args:
        context_dict (dict): dict of {context_config_key : context_config_value}
    """
    if "output_preset" in context_dict:
        with open(os.path.join(get_project_root(), "sibyl", "db", "output_presets.yml"), "r") as f:
            output_preset_dict = yaml.safe_load(f)
        if context_dict["output_preset"] in output_preset_dict:
            config_values = output_preset_dict[context_dict["output_preset"]]
            for config_name in config_values:
                if config_name not in output_preset_dict:
                    context_dict[config_name] = config_values[config_name]

    schema.Context.insert(config=context_dict)


def insert_entities_from_csv(
    filename, label_column=None, max_entities=None, pbar=None, total_time=30
):
    """
    Insert entities from a csv file into the database.
    Required columns:
        - eid: the entity id
        - [feature1, feature2, ...]: the feature values of the entity
    Optional columns:
        - row_id: the row_ids of each row
        - [label_column]: the label (y-value) of the row
    Args:
        filename (string): Filepath of csv file
        label_column (string): Name of the column containing labels (y-values)
        max_entities (int): Maximum number of entities to insert
        pbar (tqdm): tqdm progress bar
        total_time (int): Total ticks to allocate to this function on pbar

    Returns:
        list: List of eids inserted
    """
    try:
        entity_df = pd.read_csv(filename)
    except FileNotFoundError:
        raise FileNotFoundError(f"Entities file {filename} not found. Must provide valid file.")

    return insert_entities_from_dataframe(entity_df, label_column, max_entities, pbar, total_time)


def insert_entities_from_dataframe(
    entity_df, label_column=None, max_entities=None, pbar=None, total_time=30
):
    """
    Insert entities from a pandas Dataframe into the database.
    Required columns:
        - eid: the entity id
        - [feature1, feature2, ...]: the feature values of the entity
    Optional columns:
        - row_id: the row_ids of each row
        - [label_column]: the label (y-value) of the row
    Args:
        entity_df (Dataframe): Dataframe of entity information
        label_column (string): Name of the column containing labels (y-values)
        max_entities (int): Maximum number of entities to insert
        pbar (tqdm): tqdm progress bar
        total_time (int): Total ticks to allocate to this function on pbar

    Returns:
        list: List of eids inserted
    """
    if max_entities is not None:
        if max_entities < entity_df.shape[0]:
            entity_df = entity_df.sample(max_entities)
    eids = entity_df["eid"]

    if "row_id" not in entity_df:
        entity_df["row_id"] = pd.Series(np.arange(0, entity_df.shape[0])).astype(str)
        use_rows = False
    else:
        entity_df["row_id"] = entity_df["row_id"].astype(str)
        use_rows = True

    entity_df = entity_df.set_index(["eid", "row_id"])
    raw_entities = {
        level: entity_df.xs(level).to_dict("index") for level in entity_df.index.levels[0]
    }

    entities = []
    for i, eid in enumerate(raw_entities):
        entity = {"eid": str(eid), "row_ids": list(raw_entities[eid].keys())}
        targets = {}
        for row_id in raw_entities[eid]:
            if label_column in raw_entities[eid][row_id]:
                targets[row_id] = raw_entities[eid][row_id].pop(label_column)
        entity["features"] = raw_entities[eid]
        entity["labels"] = targets
        entities.append(entity)
        if pbar is not None:
            pbar.update(total_time / len(raw_entities))
    schema.Entity.insert_many(entities)
    return eids


def insert_training_set(eids, label_column):
    """
    Insert a training set (set of eids to train on) into the database.

    Args:
        eids (list): list of eids
        label_column (string): Name of the column containing labels (y-values)

    Returns:
        TrainingSet: TrainingSet object inserted
    """
    references = [schema.Entity.find_one(eid=str(eid)) for eid in eids]
    training_set = {"entities": references, "target": label_column}

    set_doc = schema.TrainingSet.insert(**training_set)
    return set_doc


def insert_model_from_file(
    filename,
    model_id=None,
    model_description="",
    model_performance="",
    fit_explainers=False,
    training_set=None,
    training_df=None,
    label_column="label",
    training_size=None,
    fit_se=True,
    validate=True,
):
    """
    Insert a model (RealApp) into the database from a pickle file.

    Args:
        filename (string): Filepath of pickled RealApp object
        fit_explainers (bool): Whether to fit explainers on the training set.
            If True, one of training_set or training_df must be provided
        training_set (TrainingSet): TrainingSet object to fit explainers with.
            Must be provided if fit_se=False
        training_df (DataFrame): Training dataframe to fit explainers with.
            Not used if training_set is provided
        label_column (string): Name of the column containing labels (y-values) in training_df
        model_id (string): Name of the model
        model_description (string): Description of the model
        model_performance (string): Performance description of the model
        training_size (int): Number of training examples to use for fitting explainers
        fit_se (bool): Whether to fit similar examples on the training set. The similar examples
            explainer is very large when fit and may not fit in the database; if this is the case,
            set fit_se to False.
        validate (bool): Whether to validate the model and explainer by running predict and explain

    Returns:
        RealApp: the RealApp object inserted, possibly fit
    """
    try:
        with open(filename, "rb") as realapp_file:
            realApp = pickle.load(realapp_file)
            realApp.id_column = "eid"
    except FileNotFoundError:
        raise FileNotFoundError(f"RealApp file {filename} not found. ")

    return insert_model_from_object(
        realApp,
        model_id=model_id,
        model_description=model_description,
        model_performance=model_performance,
        fit_explainers=fit_explainers,
        training_set=training_set,
        training_df=training_df,
        label_column=label_column,
        training_size=training_size,
        fit_se=fit_se,
        validate=validate,
    )


def insert_model_from_object(
    realApp,
    model_id=None,
    model_description="",
    model_performance="",
    fit_explainers=False,
    training_set=None,
    training_df=None,
    label_column="label",
    training_size=None,
    fit_se=True,
    validate=True,
):
    """
    Insert a model (RealApp) into the database from a pickle file.

    Args:
        realApp (RealApp): RealApp object to insert
        fit_explainers (bool): Whether to fit explainers on the training set.
            If True, one of training_set or training_df must be provided
        training_set (TrainingSet): TrainingSet object to fit explainers with.
            Must be provided if fit_se=False
        training_df (DataFrame): Training dataframe to fit explainers with.
            Not used if training_set is provided
        label_column (string): Name of the column containing labels (y-values) in training_df
        model_id (string): Name of the model
        model_description (string): Description of the model
        model_performance (string): Performance description of the model
        training_size (int): Number of training examples to use for fitting explainers
        fit_se (bool): Whether to fit similar examples on the training set. The similar examples
            explainer is very large when fit and may not fit in the database; if this is the case,
            set fit_se to False.
        validate (bool): Whether to validate the model and explainer by running predict and explain

    Returns:
        RealApp: the RealApp object inserted, possibly fit
    """
    if model_id is None:
        model_id = "model"

    if not fit_se and training_set is None:
        raise ValueError(
            "Must provide training_set to fit similar examples explainer with if not fit at"
            " database preprocessing time."
        )

    if fit_explainers or validate:
        if training_set is not None:
            df = training_set.to_dataframe()
            y_train = df["y"]
            x_train_orig = df.drop(columns="y")
        elif training_df is not None:
            y_train = training_df[label_column]
            x_train_orig = training_df.drop(columns=label_column)
        else:
            error_message = "Must provide training set or training dataframe if {}=True.".format(
                "fit_explainers" if fit_explainers else "validate"
            )
            raise ValueError(error_message)

        if fit_explainers:
            realApp.prepare_feature_contributions(
                x_train_orig=x_train_orig,
                y_train=y_train,
                training_size=training_size,
            )
            realApp.prepare_feature_importance(
                model_id=0,
                x_train_orig=x_train_orig,
                y_train=y_train,
                training_size=training_size,
            )
            if fit_se:
                realApp.prepare_similar_examples(
                    model_id=0,
                    x_train_orig=x_train_orig,
                    y_train=y_train,
                    training_size=training_size,
                    standardize=True,
                )
        if validate:
            # Check that everything is working correctly
            _validate_model_and_explainer(realApp, x_train_orig)

    explainer_serial = pickle.dumps(realApp)

    importance_dict = realApp.produce_feature_importance()
    importance_df = pd.DataFrame.from_dict(importance_dict)
    importance_df = importance_df.rename(
        columns={"Feature Name": "name", "Importance": "importance"}
    )
    importance_df.set_index("name")

    importances = importance_df.to_dict(orient="dict")["importance"]

    items = {
        "model_id": model_id,
        "importances": importances,
        "description": model_description,
        "performance": model_performance,
        "explainer": explainer_serial,
        "training_set": training_set,
    }
    schema.Model.insert(**items)
    return realApp


def prepare_database(config_file, directory=None):
    def _process_fp(fn):
        """
        Process a filename to be relative to the directory

        Args:
            fn (string): Filename

        Returns:
            string: Relative filepath
        """
        return os.path.join(directory, fn)

    times = {
        "Categories": 2,
        "Features": 3,
        "Context": 2,
        "Entities": 20,
        "Training Set": 20,
        "Model": 20,
    }
    pbar = tqdm(total=sum(times.values()))

    with open(config_file, "r") as f:
        cfg = yaml.safe_load(f)

    # Begin database loading ---------------------------
    database_name = cfg["database_name"]
    if directory is None:
        if cfg.get("directory") is None:
            directory = os.path.join(get_project_root(), "dbdata", database_name)
        else:
            directory = os.path.join(get_project_root(), "dbdata", cfg["directory"])

    if cfg.get("DROP_OLD", False):
        client = MongoClient("localhost", 27017)
        client.drop_database(database_name)
    connect(database_name, host="localhost", port=27017)

    # INSERT CATEGORIES, IF PROVIDED
    pbar.set_description("Inserting categories...")
    if cfg.get("category_fn"):
        insert_categories_from_csv(_process_fp(cfg.get("category_fn")))
    pbar.update(times["Categories"])

    # INSERT FEATURES
    pbar.set_description("Inserting features...")
    insert_features_from_csv(_process_fp(cfg.get("features_fn", "features.csv")))
    pbar.update(times["Features"])

    # INSERT ENTITIES
    pbar.set_description("Inserting entities...")
    eids = insert_entities_from_csv(
        _process_fp(cfg.get("entity_fn", "entities.csv")),
        label_column=cfg.get("target", "target"),
        pbar=pbar,
        total_time=times["Entities"],
    )

    # INSERT CONTEXT
    pbar.set_description("Inserting context...")
    insert_context_from_yaml(_process_fp(cfg.get("context_config_fn")))
    pbar.update(times["Context"])

    # INSERT FULL DATASET
    pbar.set_description("Inserting training set...")
    if cfg.get("include_database", False) and cfg.get("training_entities_fn"):
        eids = insert_entities_from_csv(
            _process_fp(cfg.get("training_entities_fn")),
            label_column=cfg.get("target", "target"),
            pbar=pbar,
            total_time=times["Training Set"],
        )
    else:
        pbar.update(times["Training Set"])
    set_doc = insert_training_set(eids, cfg.get("target"))

    # INSERT MODEL
    pbar.set_description("Inserting model...")
    if cfg.get("explainer_directory_name"):
        explainer_directory = _process_fp(cfg.get("explainer_directory_name"))
        if not os.path.isdir(explainer_directory):
            raise FileNotFoundError(
                f"Explainer directory {explainer_directory} is not a valid directory."
            )
        number_of_explainers = len(os.listdir(explainer_directory))
        for i, explainer_file in enumerate(os.listdir(explainer_directory)):
            if explainer_file.endswith(".pkl"):  # Ignore other files in the directory
                insert_model(
                    _process_fp(
                        cfg.get("training_entities_fn") or cfg.get("entity_fn") or "entities.csv"
                    ),
                    cfg.get("target", "target"),
                    set_doc,
                    explainer_fp=os.path.join(explainer_directory, explainer_file),
                    model_id=explainer_file[:-4],
                    training_size=cfg.get("training_size"),
                    fit_explainers=cfg.get("fit_explainers", False),
                    fit_se=cfg.get("fit_se", True),
                )
            pbar.update(times["Model"] / number_of_explainers)
    else:
        insert_model(
            _process_fp(cfg.get("training_entities_fn") or cfg.get("entity_fn") or "entities.csv"),
            cfg.get("target", "target"),
            set_doc,
            explainer_fp=_process_fp(cfg.get("explainer_fn")),
            model_id=cfg.get("model_name"),
            training_size=cfg.get("training_size"),
            fit_explainers=cfg.get("fit_explainers", False),
            fit_se=cfg.get("fit_se", True),
        )
        pbar.update(times["Model"])


if __name__ == "__main__":
    if len(sys.argv) == 2:
        prepare_database(sys.argv[1])
    elif len(sys.argv) == 3:
        prepare_database(sys.argv[1], sys.argv[2])
    else:
        print("Invalid arguments. Usage: python preprocessing.py CONFIG_FILE [DIRECTORY]")
