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

-   The Restful APIs documentation: http://54.208.61.79/apidoc/
-   Homepage: https://github.com/HDI-Project/sibylapp

# Overview

Interpretability is perhaps most impactful in situations where humans make decisions with input from amachine learning model. In such situations, humans have traditionally made decisions without ML models, and as such use the ML model predictions as an aideto improve their effectiveness or speed.
In these cases, explanations can serve many functions. They may help build user trust in the model, identify possible mistakes in the model’s prediction, expedite decisionmaking, maintain accountability, validate their hypotheses, or satisfy curiosity.

Sibylapp is an online interactive tool built on the top of Sibyl (python library) to provide explanations to predictive models on tabular data.

# Install

## Requirements

**sibylapp** has been developed and tested on [Python 3.5, 3.6, 3.7 and 3.8](https://www.python.org/downloads/)

Also, although it is not strictly required, the usage of a [virtualenv](https://virtualenv.pypa.io/en/latest/)
is highly recommended in order to avoid interfering with other software installed in the system
in which **sibylapp** is run.

These are the minimum commands needed to create a virtualenv using python3.6 for **sibylapp**:

```bash
pip install virtualenv
virtualenv -p $(which python3.6) sibylapp-venv
```

Afterwards, you have to execute this command to activate the virtualenv:

```bash
source sibylapp-venv/bin/activate
```

Remember to execute it every time you start a new console to work on **sibylapp**!

<!-- Uncomment this section after releasing the package to PyPI for installation instructions
## Install from PyPI

After creating the virtualenv and activating it, we recommend using
[pip](https://pip.pypa.io/en/stable/) in order to install **sibylapp**:

```bash
pip install sibylapp
```

This will pull and install the latest stable release from [PyPI](https://pypi.org/).
-->

## Install from source

With your virtualenv activated, you can clone the repository and install it from
source by running `make install` on the `stable` branch:

```bash
git clone git@github.com:HDI-Project/sibylapp.git
cd sibylapp
git checkout stable
make install
```

## Install for Development

If you want to contribute to the project, a few more steps are required to make the project ready
for development.

Please head to the [Contributing Guide](https://HDI-Project.github.io/sibylapp/contributing.html#get-started)
for more details about this process.

# Quickstart

In this short tutorial we will guide you through a series of steps that will help you
getting started with **sibylapp**.

TODO: Create a step by step guide here.

# What's next?

For more details about **sibylapp** and all its possibilities
and features, please check the [documentation site](https://HDI-Project.github.io/sibylapp/).
