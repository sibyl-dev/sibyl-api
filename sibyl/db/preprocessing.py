import os
import pickle
import sys

import numpy as np
import pandas as pd
import yaml
from mongoengine import connect, disconnect
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


def _validate_model_and_realapp(realapp, train_dataset):
    """
    Run predict and explain processes to make sure everything is working correctly
    """
    realapp.predict(train_dataset.iloc[0:2])
    realapp.produce_feature_contributions(train_dataset.iloc[0:2])


def connect_to_db(database_name, drop_old=False):
    """
    Connect to database_name
    Args:
        database_name (string): Name of database to connect to
        drop_old (bool): Whether to drop the database if it already exists
    """
    if drop_old:
        client = MongoClient("localhost", 27017)
        client.drop_database(database_name)
    connect(database_name, host="localhost", port=27017)


def disconnect_from_db():
    """
    Disconnect from the database
    """
    disconnect()


def get_entities_df():
    """
    Get entities dataframe from database
    """
    entities = schema.Entity.find(as_df_=True)
    if len(entities) == 0:
        return pd.DataFrame()
    feature_dict = entities.set_index("eid")["features"].to_dict()
    feature_df = pd.DataFrame.from_dict(
        {(i, j): feature_dict[i][j] for i in feature_dict.keys() for j in feature_dict[i].keys()},
        orient="index",
    )
    label_dict = entities.set_index("eid")["labels"].to_dict()
    label_df = pd.DataFrame.from_dict(
        {(i, j): label_dict[i][j] for i in label_dict.keys() for j in label_dict[i].keys()},
        orient="index",
        columns=["label"],
    )
    df = pd.concat([feature_df, label_df], axis=1)
    df.insert(0, "eid", df.index.get_level_values(0))
    df.insert(1, "row_id", df.index.get_level_values(1))
    return df.reset_index(drop=True)


def get_features_df():
    """
    Get features dataframe from database
    """
    features = schema.Feature.find(as_df_=True)
    features = features[
        features.columns
        & ["name", "description", "category", "type", "negated_description", "values"]
    ]
    if len(features) == 0:
        return pd.DataFrame()
    return features


def get_context_dict():
    """
    Get context dictionary from database
    """
    context = schema.Context.find().first()
    if len(context) == 0:
        return {}
    return context["config"]


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
        - type: the type of the feature, one of "numeric", "categorical", "boolean"
    Optional columns:
        - description: a description of the feature
        - negated_description: a description of the feature when it is negated
        - category: the category of the feature, as in the category table

    Args:
        features_df (DataFrame): Dataframe of feature information

    Returns:
        list: List of feature names inserted
    """
    features_df = features_df.replace(np.nan, None)
    if "category" in features_df:
        categories = set(features_df["category"])
        already_inserted_categories = schema.Category.find(as_df_=True, only_=["name"])
        if not already_inserted_categories.empty:
            already_inserted_categories = set(already_inserted_categories["name"])
        new_categories = [
            {"name": cat} for cat in categories if cat not in already_inserted_categories
        ]
        if len(new_categories) > 0:
            schema.Category.insert_many(new_categories)

    items = features_df.to_dict(orient="records")
    if len(items) == 0:
        return []
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
    if "name" not in category_df:
        raise ValueError("Category dataframe must contain column 'name' at a minimum.")
    items = category_df.to_dict(orient="records")
    if len(items) == 0:
        return []
    schema.Category.insert_many(items)
    return category_df["name"].tolist()


def insert_context_from_yaml(filepath, context_id="context"):
    """
    Insert context from a yaml file into the database.
    See sibyl/templates/context_config_template.yml for an example of the format.

    Args:
        filepath (string): Filepath of yaml file containing context information
        context_id (string): name of context to add
    """
    if filepath is None:
        return
    try:
        context_dict = yaml.safe_load(open(filepath, "r"))
    except FileNotFoundError:
        raise FileNotFoundError(f"Context config file {filepath} not found. ")

    return insert_context_from_dict(context_dict, context_id)


def insert_context_from_dict(context_dict, context_id="context"):
    """
    Insert context from a python dictionary into the database.
    See sibyl/templates/context_config_template.yml for an example of config options.

    Args:
        context_dict (dict): dict of {context_config_key : context_config_value}
        context_id (string): name of context to add
    """
    if "output_preset" in context_dict:
        with open(os.path.join(get_project_root(), "sibyl", "db", "output_presets.yml"), "r") as f:
            output_preset_dict = yaml.safe_load(f)
        if context_dict["output_preset"] in output_preset_dict:
            config_values = output_preset_dict[context_dict["output_preset"]]
            for config_name in config_values:
                if config_name not in output_preset_dict:
                    context_dict[config_name] = config_values[config_name]

    schema.Context.insert(context_id=context_id, config=context_dict)


def insert_entities_from_csv(
    filename, label_column=None, max_entities=None, update_feature_values=False
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
        update_feature_values (bool):
            Whether to update feature documents with the values in these entities

    Returns:
        list: List of eids inserted
    """
    try:
        entity_df = pd.read_csv(filename)
    except FileNotFoundError:
        raise FileNotFoundError(f"Entities file {filename} not found. Must provide valid file.")

    return insert_entities_from_dataframe(
        entity_df, label_column, max_entities, update_feature_values
    )


def insert_entities_from_dataframe(
    entity_df, label_column="label", max_entities=None, update_feature_values=False
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
        update_feature_values (bool):
            Whether to update feature documents with the values in these entities

    Returns:
        list: List of eids inserted
    """
    if entity_df.empty:
        return []

    if "eid" not in entity_df:
        raise ValueError("Entity dataframe must contain column 'eid' at a minimum.")

    if entity_df.shape[1] < 2:
        raise ValueError("Entity dataframe must contain at least one feature column.")

    if max_entities is not None:
        if max_entities < entity_df.shape[0]:
            entity_df = entity_df.sample(max_entities, ignore_index=True)

    eids = entity_df["eid"]

    if "row_id" not in entity_df:
        entity_df["row_id"] = pd.Series(np.arange(0, entity_df.shape[0])).astype(str)
        use_rows = False
    else:
        entity_df["row_id"] = entity_df["row_id"].astype(str)
        use_rows = True

    if update_feature_values:
        feature_df = schema.Feature.find(as_df_=True, only_=["name", "type"])
        if not feature_df.empty:
            cat_features = feature_df["name"][feature_df["type"] == "categorical"]
            cat_feature_values = entity_df[cat_features]
            cat_feature_values = cat_feature_values.apply(
                lambda col: col.dropna().unique().astype(str)
            )
            for feature in cat_features:
                doc = schema.Feature.find(name=feature).first()
                existing_values = doc.values if doc.values is not None else []
                doc.values = existing_values + cat_feature_values[feature].tolist()
                doc.save()
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
    schema.Entity.insert_many(entities)
    return eids.tolist()


def insert_training_set(eids):
    """
    Insert a training set (set of eids to train on) into the database.

    Args:
        eids (list): list of eids

    Returns:
        TrainingSet: TrainingSet object inserted
    """
    if len(eids) == 0:
        raise ValueError("Must provide at least one eid to insert training set.")
    references = [schema.Entity.find_one(eid=str(eid)) for eid in eids]
    training_set = {"entities": references}

    set_doc = schema.TrainingSet.insert(**training_set)
    return set_doc


def insert_model_from_file(
    filename,
    model_id=None,
    model_description="",
    model_performance="",
    fit_explainers=True,
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
        validate (bool): Whether to validate the model and realapp by running predict and explain

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
    realapp,
    model_id=None,
    model_description="",
    model_performance="",
    fit_explainers=True,
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
        realapp (RealApp): RealApp object to insert
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
            realapp.prepare_feature_contributions(
                x_train_orig=x_train_orig,
                y_train=y_train,
                training_size=training_size,
            )
            realapp.prepare_feature_importance(
                model_id=0,
                x_train_orig=x_train_orig,
                y_train=y_train,
                training_size=training_size,
            )
            if fit_se:
                realapp.prepare_similar_examples(
                    model_id=0,
                    x_train_orig=x_train_orig,
                    y_train=y_train,
                    training_size=training_size,
                    standardize=True,
                )
        if validate:
            # Check that everything is working correctly
            _validate_model_and_realapp(realapp, x_train_orig)

    realapp_serial = pickle.dumps(realapp)

    importance_dict = realapp.produce_feature_importance()
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
        "realapp": realapp_serial,
        "training_set": training_set,
    }
    schema.Model.insert(**items)
    return realapp


def insert_models_from_directory(
    directory,
    fit_explainers=True,
    training_set=None,
    training_df=None,
    label_column="label",
    training_size=None,
    fit_se=True,
    validate=True,
):
    """
    Insert multiple models (RealApp) into the database from a directory of pickle files.
    Sets the model names to the filenames

    Args:
        directory (string): Directory path
        fit_explainers (bool): Whether to fit explainers on the training set.
            If True, one of training_set or training_df must be provided
        training_set (TrainingSet): TrainingSet object to fit explainers with.
            Must be provided if fit_se=False
        training_df (DataFrame): Training dataframe to fit explainers with.
            Not used if training_set is provided
        label_column (string): Name of the column containing labels (y-values) in training_df
        training_size (int): Number of training examples to use for fitting explainers
        fit_se (bool): Whether to fit similar examples on the training set. The similar examples
            explainer is very large when fit and may not fit in the database; if this is the case,
            set fit_se to False.
        validate (bool): Whether to validate the model and explainer by running predict and explain

    Returns:
        RealApp: the RealApp object inserted, possibly fit
    """
    for i, file in enumerate(os.listdir(directory)):
        if file.endswith(".pkl"):  # Ignore other files in the directory
            insert_model_from_file(
                os.path.join(directory, file),
                model_id=file[:-4],  # remove .pkl
                fit_explainers=fit_explainers,
                training_set=training_set,
                training_df=training_df,
                label_column=label_column,
                training_size=training_size,
                fit_se=fit_se,
                validate=validate,
            )


def prepare_database_from_config(config_file, directory=None):
    with open(config_file, "r") as f:
        cfg = yaml.safe_load(f)

    if "database_name" not in cfg:
        raise ValueError("Must provide database_name in config file.")

    if directory is None:
        if cfg.get("directory") is None:
            directory = os.path.join(get_project_root(), "dbdata", cfg["database_name"])
        else:
            directory = os.path.join(get_project_root(), "dbdata", cfg["directory"])

    prepare_database(
        cfg["database_name"],
        directory=directory,
        drop_old=cfg.get("drop_old", False),
        category_filepath=cfg.get("category_fn"),
        features_filepath=cfg.get("feature_fn", "features.csv"),
        entities_filepath=cfg.get("entity_fn", "entities.csv"),
        label_column=cfg.get("label_column", "label"),
        context_filepath=cfg.get("context_config_fn"),
        use_entities_as_training_set=True,
        realapp_filepath=cfg.get("realapp_fn"),
        realapp_directory=cfg.get("realapp_directory_name"),
        model_id=cfg.get("model_id"),
        fit_explainers=cfg.get("fit_explainers", True),
        training_size=cfg.get("training_size"),
        fit_se=cfg.get("fit_se", True),
    )


def prepare_database(
    database_name,
    directory=None,
    drop_old=False,
    features_df=None,
    features_filepath=None,
    entities_df=None,
    entities_filepath=None,
    label_column="label",
    realapp_filepath=None,
    realapp=None,
    realapp_directory=None,
    training_eids=None,
    use_entities_as_training_set=True,
    model_id=None,
    fit_explainers=True,
    training_size=None,
    fit_se=True,
    context_filepath=None,
    context_dict=None,
    category_df=None,
    category_filepath=None,
    streamlit_progress_bar_func=None,
):
    """
    Fully prepare a database from files or objects

    Args:
        database_name (string): Name of database
        directory (string): Directory where all files provided are located.
            Not required if full paths are given or filepath parameters are not used.
        drop_old (bool): If True and database already exists, drop the old database
        features_df (DataFrame): Dataframe of feature information
        features_filepath (string): Filepath of csv file containing feature information
        entities_df (DataFrame): Dataframe of entity information
        entities_filepath (string): Filepath of csv file containing entity information
        label_column (string): Name of the column containing labels (y-values) in entities_df
        realapp_filepath (string): Filepath of pickled RealApp object
        realapp (RealApp): RealApp object to insert
        realapp_directory (string): Directory path containing pickled RealApp objects
        training_eids (list): List of eids to use as the training set
        use_entities_as_training_set (bool): Whether to use the entities in
            entities_df/entities_filepath as the training set
        model_id (string): Name of the model
        fit_explainers (bool): Whether to fit explainers on the training set.
        training_size (int): Number of training examples to use for fitting explainers
        fit_se (bool): Whether to fit similar examples on the training set. The similar examples
            explainer is very large when fit and may not fit in the database; if this is the case,
            set fit_se to False.
        context_filepath (string): Filepath of yaml file containing context information
        context_dict (dict): dict of {context_config_key : context_config_value}
        category_df (DataFrame): Dataframe of category information
        category_filepath (string): Filepath of csv file containing category information
        streamlit_progress_bar_func (function): Streamlit progress bar function to pass in for GUI
            applications. Should generally be kept as None
    """

    def _process_fp(fn):
        """
        Process a filename to be relative to the directory

        Args:
            fn (string): Filename

        Returns:
            string: Relative filepath
        """
        if directory is None:
            return fn
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

    # Begin database loading ---------------------------
    connect_to_db(database_name, drop_old=drop_old)

    # INSERT CATEGORIES, IF PROVIDED
    pbar.set_description("Inserting categories...")
    if streamlit_progress_bar_func is not None:
        streamlit_progress_bar_func(0, "Inserting categories...")
    if category_df is not None:
        insert_categories_from_dataframe(category_df)
    elif category_filepath is not None:
        insert_categories_from_csv(_process_fp(category_filepath))
    pbar.update(times["Categories"])

    # INSERT FEATURES
    pbar.set_description("Inserting features...")
    if streamlit_progress_bar_func is not None:
        streamlit_progress_bar_func(5, "Inserting features...")
    if features_df is not None:
        insert_features_from_dataframe(features_df)
    elif features_filepath is not None:
        insert_features_from_csv(_process_fp(features_filepath))
    pbar.update(times["Features"])

    # INSERT CONTEXT
    pbar.set_description("Inserting context...")
    if streamlit_progress_bar_func is not None:
        streamlit_progress_bar_func(15, "Inserting context...")
    if context_dict is not None:
        insert_context_from_dict(context_dict)
    elif context_filepath is not None:
        insert_context_from_yaml(_process_fp(context_filepath))
    pbar.update(times["Context"])

    # INSERT ENTITIES
    pbar.set_description("Inserting entities...")
    if streamlit_progress_bar_func is not None:
        streamlit_progress_bar_func(20, "Inserting entities...")
    eids = None
    if entities_df is not None:
        eids = insert_entities_from_dataframe(
            entities_df, label_column=label_column, update_feature_values=True
        )
    elif entities_filepath is not None:
        eids = insert_entities_from_csv(
            _process_fp(entities_filepath), label_column=label_column, update_feature_values=True
        )
    pbar.update(times["Entities"])

    # INSERT FULL DATASET
    pbar.set_description("Inserting training set...")
    if streamlit_progress_bar_func is not None:
        streamlit_progress_bar_func(50, "Inserting training set...")
    training_set = None
    if training_eids is not None:
        training_set = insert_training_set(training_eids)
    elif use_entities_as_training_set:
        if eids is None:
            raise ValueError("Must provide entities or set use_entities_as_training_set=False")
        training_set = insert_training_set(eids)
    pbar.update(times["Training Set"])

    # INSERT MODEL
    pbar.set_description("Inserting model...")
    if streamlit_progress_bar_func is not None:
        streamlit_progress_bar_func(80, "Inserting model...")
    if realapp_directory is not None:
        realapp_directory = _process_fp(realapp_directory)
        if not os.path.isdir(realapp_directory):
            raise FileNotFoundError(
                f"RealApp directory {realapp_directory} is not a valid directory."
            )
        insert_models_from_directory(
            realapp_directory,
            fit_explainers=fit_explainers,
            training_set=training_set,
            training_size=training_size,
            fit_se=fit_se,
        )
    elif realapp is not None:
        insert_model_from_object(
            realapp,
            model_id=model_id,
            fit_explainers=fit_explainers,
            training_set=training_set,
            training_size=training_size,
            fit_se=fit_se,
        )
    elif realapp_filepath is not None:
        insert_model_from_file(
            _process_fp(realapp_filepath),
            model_id=model_id,
            fit_explainers=fit_explainers,
            training_set=training_set,
            training_size=training_size,
            fit_se=fit_se,
        )
    pbar.update(times["Model"])
    if streamlit_progress_bar_func is not None:
        streamlit_progress_bar_func(100, "Finalizing...")


if __name__ == "__main__":
    connect_to_db("housing")
    get_entities_df()
    if len(sys.argv) == 2:
        prepare_database_from_config(sys.argv[1])
    elif len(sys.argv) == 3:
        prepare_database_from_config(sys.argv[1], sys.argv[2])
    else:
        print("Invalid arguments. Usage: python preprocessing.py CONFIG_FILE [DIRECTORY]")
