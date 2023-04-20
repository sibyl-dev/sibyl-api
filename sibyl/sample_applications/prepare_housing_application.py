from pyreal.sample_applications import ames_housing
from pyreal import RealApp
import pickle

x_orig, y_orig = ames_housing.load_data(include_targets=True)
if "Id" in x_orig:  # TODO: remove once fixed in Pyreal's data
    x_orig = x_orig.drop("Id", axis="columns")
transformers = ames_housing.load_transformers()
model = ames_housing.load_model()

explainer = RealApp(model, X_train_orig=x_orig, y_orig=y_orig, transformers=transformers)

pickle.dump(model, open("housing/model.pkl", "wb"))
pickle.dump(explainer, open("housing/explainer.pkl", "wb"))
