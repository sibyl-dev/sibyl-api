<p align="left">
<img width=15% src="https://dai.lids.mit.edu/wp-content/uploads/2018/06/Logo_DAI_highres.png" alt=“DAI-Lab” />
<i>An open source project from Data to AI Lab at MIT.</i>
</p>

<!-- Uncomment these lines after releasing the package to PyPI for version and downloads badges -->
<!--[![PyPI Shield](https://img.shields.io/pypi/v/sibylapp.svg)](https://pypi.python.org/pypi/sibylapp)-->
<!--[![Downloads](https://pepy.tech/badge/sibylapp)](https://pepy.tech/project/sibylapp)-->

[![Travis CI Shield](https://travis-ci.org/HDI-Project/sibylapp.svg?branch=master)](https://travis-ci.org/HDI-Project/sibylapp)
[![Coverage Status](https://codecov.io/gh/HDI-Project/sibylapp/branch/master/graph/badge.svg)](https://codecov.io/gh/HDI-Project/sibylapp)

# Sibyl-API

APIs for explainable ML.

-   API Documentation: [https://sibyl-ml.dev/sibyl-api/](https://sibyl-ml.dev/sibyl-api/)

# Overview

Interpretability is perhaps most impactful in situations where humans make decisions with input from amachine learning model. In such situations, humans have traditionally made decisions without ML models, and as such use the ML model predictions as an aideto improve their effectiveness or speed.
In these cases, explanations can serve many functions. They may help build user trust in the model, identify possible mistakes in the model’s prediction, expedite decisionmaking, maintain accountability, validate their hypotheses, or satisfy curiosity.

Sibylapp is an online interactive tool built on the top of Sibyl (python library) to provide explanations to predictive models on tabular data.

# Install

## Requirements

**Sibyl-API** has been developed and tested on [Python 3.9, 3.10, and 3.11](https://www.python.org/downloads/), and on [MongoDB version 6 and 7](https://www.mongodb.com/try/download/community).

To install MongoDB, follow the instructions
[here](https://www.mongodb.com/docs/manual/administration/install-community/).

## Install from PyPi

Sibyl-API can be installed from pypi:
```bash
pip install sibyl-api
```

## Install from source

Sibyl-API uses **Poetry** for dependency management. If you do not have *Poetry* installed, please head to [poetry installation guide](https://python-poetry.org/docs/#installation)
and install poetry according to the instructions.
Run the following command to make sure poetry is activated. You may need to close and reopen the terminal.

```bash
poetry --version
```

Then, you can clone this repository and install it from
source by running `poetry install`:

```bash
git clone https://github.com/sibyl-dev/sibyl-api.git
cd sibyl-api
poetry install
```

# Quickstart
Follow these steps to get started with the built-in Ames Housing dataset example.
You can prepare and load the Ames Housing dataset by running
```bash
sibyl prepare-sample-db
```
> ⚠️ This function will overwrite any
existing database on localhost:27017 with the name **housing**):


You can now run Sibyl-API with the sample dataset with:
```bash
poetry run sibyl run -D housing -v
```

Once Sibyl-API is running, you can access and test your APIs manually at `localhost:3000/apidocs`

# Preparing database
Sibyl-API uses a MongoDB-based database system. We offer several methods to setup your database.

## Preparing data
### Required inputs
At minimum, sibyl-API requires the following inputs (either as a DataFrame or csv, see creation options below):

**entities**: A table with the entities to be explained. Each row should correspond to a single observation.

Columns:
  - `eid` (*required*): unique identifier specifying which entity this observation corresponds to
  - `row_id`: unique identifier specifying the observation ID. Together, `eid` and `row_id` should uniquely identify each observation.
  - `label`: the ground-truth label for this observation
  - `[FEATURES]`: additional columns for each feature used to make predictions. These columns should be named the same as the features used in the model.

Sample table:

| `eid`   | `row_id` | `label` | `feature1` | `feature2` | `feature3` |
|---------|----------|---------|------------|------------|------------|
| entity1 | 101      | 0       | 0.1        | 0.2        | 0.3        |
| entity1 | 102      | 1       | 0.2        | 0.3        | 0.4        |
| entity2 | 204      | 1       | 0.3        | 0.4        | 0.5        |

**features**: A table with the features used to make predictions. Each row should correspond to a single feature.

Columns:
  - `feature` (*required*): the name of the feature
  - `type` (*required*): the type of the feature. This can be `categorical`, `numerical`, or `boolean`
  - `description`: a description of the feature
  - `negative_description`: a description of the feature when it is not present. Only for boolean features
  - `values`: a list of possible values for the feature. Only for categorical features.

Sample table:

| `feature` | `type` | `description`        | `negative_description`         | `values`                    |
|-----------|--------|----------------------|--------------------------------|-----------------------------|
| size      | numerical | size in square feet  |                                |                             |
| has_ac    | boolean | has air conditioning | does not have air conditioning |                             |
| nghbrh    | categorical | neighborhood         |                                | [Oceanview, Ridge, Oakvale] |

**realapp**: A pickled `pyreal.RealApp` object. This object is used to generate explanations for the model.

### Optional inputs
Additionally, you can configure APIs futher with:

**config**: a configuration file (YAML or python dictionary) specifying
additional settings. See `sibyl/db/config_template.yml` for options.

**categories**: a table with the categories used to make predictions. Each row should correspond to a single category.

Columns:
  - `category` (*required*): the name of the category
  - `description`: a description of the category
  - `color`: color to use for the category
  - `abbreviation`: abbreviation to use for the category

## Creating the Mongo database

### With the prepare-db script
Be sure to `start` your mongodb service before preparing the database

Copy `sibyl/db/config_template.yml` and fill it in with your configurations. Place required data
in a common directory.

Next, run the preprocessing script with:
```bash
sibyl run prepare-db [CONFIG_NAME].yml [DIRECTORY]
```
where `[CONFIG_NAME].yml` is the path to your configuration file and `[DIRECTORY]` is
the directory containing your data.

### With the Setup Wizard
Currently, the setup wizard is only available when installing from source.
First, install the optional setup dependencies with
```bash
poetry install --with setup
```
Then, run the setup wizard with
```bash
poetry run streamlit run setup-wizard/main.py
```

# Running APIs

Once the library has been installed, you can run the APIs locally with:

```bash
poetry run sibyl run -v -D [DATABASE_NAME]
```

Or, to run in development mode:
```bash
poetry shell

sibyl run -E development -v -D [DATABASE_NAME]
```

You can then access your APIs locally at http://localhost:3000/apidocs

# Contributing Guide
We appreciate contributions of all kinds! To contribute code to the repo please follow these steps:
1. Clone and install the library and load in your test database(s) following the instructions above.
2. Make a new branch off of `dev` with a descriptive name describing your change.
3. Make changes to that branch, committing and pushing code as you go.
4. Run the following commands to ensure your code passed required code style guidelines and tests:
```
# Run all tests
poetry run invoke test

# Run unit tests only
poetry run invoke test-unit

# Fix most linting errors
poetry run invoke fix-lint

# Ensure no linting errors remain
poetry run invoke lint
```
5. You can manually run `sibyl/test_apis_on_database.ipynb` on your database(s) to test further.
6. Before making a PR with your final changes, update the api docs by running Sibyl with the -G flag, ie.
```
# Generate docs
poetry run sibyl run -G
```
8. Once all tests/linting pass, push all code and make a pull request. One all checks pass and the PR has been approved, merge your code and delete the branch.
