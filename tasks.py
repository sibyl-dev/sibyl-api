import subprocess
import webbrowser
import shutil

from pathlib import Path
from invoke import task
from sys import executable
import os

from sibyl.db.preprocessing import prepare_database_from_config
from sibyl.sample_applications import prepare_housing_application
from sibyl.utils import get_project_root
import yaml


def print_red(s):
    print("\033[91m {}\033[00m".format(s), end="")


def print_green(s):
    print("\033[92m {}\033[00m".format(s), end="")


def _rm_recursive(path: Path, pattern: str):
    """
    Glob the given relative pattern in the directory represented by this path,
        calling shutil.rmtree on them all
    """

    for p in path.glob(pattern):
        shutil.rmtree(p, ignore_errors=True)


@task
def clean_build(context):
    """
    Cleans the build
    """

    shutil.rmtree(Path("build"), ignore_errors=True)
    shutil.rmtree(Path("dist"), ignore_errors=True)
    shutil.rmtree(Path(".eggs"), ignore_errors=True)

    _rm_recursive(Path("."), "**/*.egg-info")
    _rm_recursive(Path("."), "**/*.egg")


@task
def clean_coverage(context):
    """
    Cleans the coverage results
    """

    Path(".coverage").unlink(missing_ok=True)

    for path in Path(".").glob(".coverage.*"):
        path.unlink(missing_ok=True)

    shutil.rmtree(Path("htmlcov"), ignore_errors=True)


@task
def clean_docs(context):
    for path in Path("docs/api").glob("*.rst"):
        path.unlink(missing_ok=True)

    subprocess.run(["sphinx-build", "-M", "clean", ".", "_build"], cwd=Path("docs"))


@task
def clean_pyc(context):
    """
    Cleans compiled files
    """

    _rm_recursive(Path("."), "**/*.pyc")
    _rm_recursive(Path("."), "**/*.pyo")
    _rm_recursive(Path("."), "**/*~")
    _rm_recursive(Path("."), "**/__pycache__")


@task
def clean_test(context):
    """
    Cleans the test store
    """

    shutil.rmtree(Path(".pytest_cache"), ignore_errors=True)


@task
def coverage(context):
    """
    Runs the unit test coverage analysis
    """

    subprocess.run(["coverage", "run", "--source", "sibyl", "-m", "pytest"])
    subprocess.run(["coverage", "report", "-m"])
    subprocess.run(["coverage", "html"])

    url = os.path.join("htmlcov", "index.html")
    webbrowser.open(url)


@task
def docs(context):
    """
    Cleans the doc builds and builds the docs
    """

    clean_docs(context)

    subprocess.run(["sphinx-build", "-b", "html", ".", "_build"], cwd=Path("docs"))


@task
def fix_lint(context):
    """
    Fixes all linting and import sort errors. Skips init.py files for import sorts
    """

    subprocess.run(["black", "sibyl"])
    subprocess.run(["black", "tests"])
    subprocess.run(["isort", "--atomic", "sibyl", "tests", "setup-wizard"])


@task
def lint(context):
    """
    Runs the linting and import sort process on all library files and tests and prints errors.
        Skips init.py files for import sorts
    """
    subprocess.run(["isort", "-c", "sibyl", "tests", "setup-wizard"], check=True)


@task
def test(context):
    """
    Runs all test commands.
    """

    failures_in = []

    try:
        test_unit(context)
    except subprocess.CalledProcessError:
        failures_in.append("Unit tests")

    try:
        test_scripts(context)
    except subprocess.CalledProcessError:
        failures_in.append("Testing scripts")

    if len(failures_in) == 0:
        print_green("\nAll tests successful :)")
    else:
        print_red("\n:( Failures in: ")
        for i in failures_in:
            print_red(i + ", ")


@task
def test_unit(context):
    """
    Runs all unit tests and outputs results and coverage
    """
    subprocess.run(["pytest", "--cov=sibyl"], check=True)


@task
def test_scripts(context):
    """
    Runs all scripts in the tutorials directory and checks for exceptions
    """

    subprocess.run(["pytest", "--nbmake", "./tests/test_on_database.ipynb"], check=True)


@task
def prepare_sample_db(context):
    """
    Load the housing sample application into the currently connected mongo database
    """
    prepare_housing_application.run()
    prepare_database_from_config(
        os.path.join(
            os.path.dirname(prepare_housing_application.__file__), "housing_prepare_db_config.yml"
        )
    )


@task
def prepare_db(context, config, directory=None):
    """
    Load a database into the currently connected mongo database
    """
    if directory is None:
        with open(config) as stream:
            db_name = yaml.safe_load(stream)["database_name"]
            directory = os.path.join(get_project_root(), "dbdata", db_name)
    prepare_database_from_config(config, directory)


@task
def view_docs(context):
    """
    Opens the docs in a browser window
    """

    docs(context)

    url = os.path.join("docs", "_build", "index.html")
    webbrowser.open(url)
