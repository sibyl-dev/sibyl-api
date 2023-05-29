import os
import pickle
import pandas as pd

from pyreal import RealApp
from pyreal.sample_applications import ames_housing
from pyreal.transformers import fit_transformers

from sibyl.utils import get_project_root

DIRECTORY = os.path.join(get_project_root(), "dbdata", "housing")

x_orig, y_orig = ames_housing.load_data(include_targets=True)
x_orig = x_orig.rename({"Id": "eid"}, axis="columns")
entities = pd.concat([x_orig, y_orig], axis=1)
entities.to_csv(os.path.join(DIRECTORY, "entities.csv"), index=False)

transformers = ames_housing.load_transformers()
fit_transformers(transformers, x_orig)

model = ames_housing.load_model()

explainer = RealApp(model, transformers=transformers, id_column="eid")
explainer.prepare_feature_contributions(x_train_orig=x_orig.drop("eid", axis="columns"), y_train=y_orig)
explainer.prepare_feature_importance(x_train_orig=x_orig.drop("eid", axis="columns"), y_train=y_orig,)

pickle.dump(model, open(os.path.join(DIRECTORY, "model.pkl"), "wb"))
pickle.dump(explainer, open(os.path.join(DIRECTORY, "explainer.pkl"), "wb"))
