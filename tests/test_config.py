# Santity tests a given config and database

from sibyl.utils import get_project_root
import os
import argparse

from sibyl.core import Sibyl
from sibyl.utils import read_config, setup_logging


def test_prep_app():
    config = read_config("./sibyl/config.yml")
    sibyl = Sibyl(config, False)
