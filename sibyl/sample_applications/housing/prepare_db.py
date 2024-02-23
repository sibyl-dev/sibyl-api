import os
import pickle

import pandas as pd
from pyreal import RealApp
from pyreal.sample_applications import ames_housing

from sibyl.db.preprocessing import prepare_database_from_config


def run():
    directory = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    x_orig, y_orig = ames_housing.load_data(include_targets=True)
    x_orig = x_orig.rename({"Id": "eid"}, axis="columns")
    entities = pd.concat([x_orig, y_orig], axis=1)
    entities.to_csv(os.path.join(directory, "entities.csv"), index=False)

    transformers = ames_housing.load_transformers()
    model = ames_housing.load_model()

    realapp = RealApp(model, transformers=transformers, id_column="eid")
    realapp.prepare_feature_contributions(
        x_train_orig=x_orig.drop("eid", axis="columns"), y_train=y_orig
    )
    realapp.prepare_feature_importance(
        x_train_orig=x_orig.drop("eid", axis="columns"),
        y_train=y_orig,
    )
    realapp.prepare_similar_examples(
        x_train_orig=x_orig.drop("eid", axis="columns"),
        y_train=y_orig,
    )
    pickle.dump(realapp, open(os.path.join(directory, "realapp.pkl"), "wb"))

    prepare_database_from_config(os.path.join(directory, "prepare_db_config.yml"), directory)
