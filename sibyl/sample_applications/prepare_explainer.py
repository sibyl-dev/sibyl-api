import pandas as pd
from pyreal.transformers import OneHotEncoder
from sklearn.linear_model import Ridge
from pyreal.transformers import run_transformers
import pickle
from pyreal import RealApp
from sibyl.sample_applications.transformers import AmesHousingImputer


data = pd.read_csv("../../dbdata/housing/entities.csv")
data = data[data.GrLivArea < 4000]
y_orig = data["SalePrice"]
x_orig = data.drop("SalePrice", axis="columns")
x_orig = x_orig.drop("eid", axis="columns")

imputer = AmesHousingImputer()
x_imputed = imputer.data_transform(x_orig)

object_columns = x_imputed.select_dtypes(include=["object"]).columns
onehotencoder = OneHotEncoder(object_columns)
onehotencoder.fit(x_imputed)

transformers = [imputer, onehotencoder]

model = Ridge()
x_model = run_transformers(transformers, x_orig)
model.fit(x_model, y_orig)

pickle.dump(model, open("../../dbdata/housing/model.pkl", "wb"))

transformers = [imputer, onehotencoder]
explainer = RealApp(model, X_train_orig=x_orig, transformers=transformers)
pickle.dump(explainer, open("../../dbdata/housing/explainer.pkl", "wb"))
