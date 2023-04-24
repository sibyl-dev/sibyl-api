<p align="left">
<img width=15% src="https://dai.lids.mit.edu/wp-content/uploads/2018/06/Logo_DAI_highres.png" alt=“DAI-Lab” />
<i>An open source project from Data to AI Lab at MIT.</i>
</p>

<!-- Uncomment these lines after releasing the package to PyPI for version and downloads badges -->
<!--[![PyPI Shield](https://img.shields.io/pypi/v/sibylapp.svg)](https://pypi.python.org/pypi/sibylapp)-->
<!--[![Downloads](https://pepy.tech/badge/sibylapp)](https://pepy.tech/project/sibylapp)-->

[![Travis CI Shield](https://travis-ci.org/HDI-Project/sibylapp.svg?branch=master)](https://travis-ci.org/HDI-Project/sibylapp)
[![Coverage Status](https://codecov.io/gh/HDI-Project/sibylapp/branch/master/graph/badge.svg)](https://codecov.io/gh/HDI-Project/sibylapp)

# sibylapp

Explanation tool for machine learning

<!-- - Documentation: https://HDI-Project.github.io/sibylapp -->

-   The Restful APIs documentation: http://18.223.186.158/
-   Homepage: https://github.com/DAI-Lab/sibylapp

# Overview

Interpretability is perhaps most impactful in situations where humans make decisions with input from amachine learning model. In such situations, humans have traditionally made decisions without ML models, and as such use the ML model predictions as an aideto improve their effectiveness or speed.
In these cases, explanations can serve many functions. They may help build user trust in the model, identify possible mistakes in the model’s prediction, expedite decisionmaking, maintain accountability, validate their hypotheses, or satisfy curiosity.

Sibylapp is an online interactive tool built on the top of Sibyl (python library) to provide explanations to predictive models on tabular data.

# Install

## Requirements

**Sibyl-API** has been developed and tested on [Python 3.8, 3.9, and 3.10](https://www.python.org/downloads/)

This library uses Poetry for package management.

## Install from source

If you do not have **poetry** installed, please head to [poetry installation guide](https://python-poetry.org/docs/#installation)
and install poetry according to the instructions.
Run the following command to make sure poetry is activated. You may need to close and reopen the terminal.

```bash
poetry --version
```

Finally, you can clone this repository and install it from
source by running `poetry install`:

```bash
git clone https://github.com/sibyl-dev/sibyl-api.git
cd sibyl-api
poetry install
```

Sibyl-API runs using MongoDB. To install, run:

```bash
pip install mongoengine
```

## Quickstart
Follow these steps to get started with the built-in Ames Housing dataset example
1. Load the housing dataset into MongoDB by running the preprocessing script with `housing_config.yml`:
```bash
poetry run python sibyl\db\preprocessing.py sibyl\sample_applications\housing_config.yml
```
2. Make sure mongodb.db in `sibyl/config.yml` is set to `housing`.
3. Run  Sibyl-API with:
```bash
poetry run sibyl run -v
```

## Preparing database
Sibyl-API uses a MongoDB-based database system. You can fill the database using the `preprocessing.py` script by
following these steps:

First, if it doesn't already exist, add a `dbdata` directory in the top-level `sibyl-api` directory.

Next, add a directory in `dbdata` named after your domain, and fill it with your data files. You should end with a file
structure that looks like:
```
sibyl-api
|---dbdata
   |---domain_name
        |---entities.csv
        |   feature.csv
        |   model.pkl
        |   ...
```

Next, copy `sibyl/db/config_template.yml` and fill it in with your file names.

Finally, run the preprocessing script with:
```bash
poetry run python preprocessing.py [CONFIG_NAME].yml
```

## Running APIs

Once the library has been installed, you can run the APIs locally with:

```bash
poetry run sibyl run -v
```

Or, to run in development mode:
```bash
poetry shell
sibyl run -E development -v
```

You can then access your APIs locally at http://localhost:3000/apidocs
