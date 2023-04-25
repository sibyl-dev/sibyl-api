# -*- coding: utf-8 -*-

"""
Data Management module.

This module contains functions that allow downloading demo data from Amazon S3,
as well as load and work with other data stored locally.

The demo data is a modified version of the NASA data found here:

https://s3-us-west-2.amazonaws.com/telemanom/data.zip
"""

import logging
import os

import requests

LOGGER = logging.getLogger(__name__)

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
BUCKET = "sibylapp"
S3_URL = "https://{}.s3.amazonaws.com/{}"
DATA_FILES = ("model_weights.csv", "tabular_data.csv", "model.pkl")


def download(name, data_path=DATA_PATH):
    """Download a data file from S3.

    If the file has never been loaded before, it will be downloaded
    from the [d3-ai-orion bucket](https://d3-ai-orion.s3.amazonaws.com) or
    the S3 bucket specified following the `s3://{bucket}/path/to/datafile` format,
    and then cached inside the `data` folder, within the `orion` package
    directory, and then returned.

    Otherwise, if it has been downloaded and cached before, it will do nothing.

    Args:
        name (str):
            Name of the file (e.g., model_weights.csv) to load.
        data_path (str):
            Path to the Folder to hold the downloaded data files.
    """

    url = None
    if name.startswith("s3://"):
        parts = name[5:].split("/", 1)
        bucket = parts[0]
        path = parts[1]
        url = S3_URL.format(bucket, path)

        filename = os.path.join(data_path, path.split("/")[-1])
    else:
        filename = os.path.join(data_path, name)

    if not os.path.exists(filename):
        url = url or S3_URL.format(BUCKET, "{}".format(filename))

        LOGGER.info("Downloading %s from %s", filename, url)
        os.makedirs(data_path, exist_ok=True)

        r = requests.get(url, allow_redirects=True)
        open(filename, "wb").write(r.content)


def download_demo():
    LOGGER.info("Downloading SibylApp Demo Data")
    for name in DATA_FILES:
        download(name)


def load_csv(path, timestamp_column=None, value_column=None):
    # header = None if timestamp_column is not None else 'infer'
    # data = pd.read_csv(path, header=header)
    pass
