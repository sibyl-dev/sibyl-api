import argparse

from sibyl.core import Sibyl
from sibyl.utils import read_config, setup_logging

from sibyl.db.preprocessing import prepare_database


def _run(args):
    config = read_config("./sibyl/config.yml")
    sibyl = Sibyl(config, args.docker, args.dbhost, args.dbport, args.db)

    sibyl.run_server(args.env, args.port)


def _prepare_db(args):
    prepare_database(args.config, args.dir)


def get_parser():
    # Common Parent - Shared options
    common = argparse.ArgumentParser(add_help=False)

    common.add_argument("-l", "--logfile", help="Name of the logfile.If not given, log to stdout.")

    common.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Be verbose. Use -vv for increased verbosity.",
    )

    common.add_argument("--docker", action="store_true", help="Deploy in docker environment")

    parser = argparse.ArgumentParser(description="Sibyl Command Line Interface.")
    parser.set_defaults(function=None)

    # sibyl [action]
    action = parser.add_subparsers(title="action", dest="action")
    action.required = True

    # sibyl run
    run = action.add_parser("run", help="Start flask server", parents=[common])
    run.set_defaults(function=_run)

    run.add_argument("-P", "--port", type=int, help="Flask server port")
    run.add_argument(
        "-E",
        "--env",
        type=str,
        help="Flask environment",
        choices=["development", "production", "test"],
    )
    run.add_argument(
        "--dbhost", action="store", help="Host address to access database. Overrides config", type=str
    )
    run.add_argument(
        "--dbport", action="store", help="Port to access database. Overrides config", type=int
    )
    run.add_argument(
        "-D", "--db", action="store", help="Database name to use. Overrides config", type=str
    )

    # sibyl load-db
    prepare_db = action.add_parser("prepare-db", help="Prepare database from config", parents=[common])
    prepare_db.set_defaults(function=_prepare_db)

    prepare_db.add_argument("config", action="store", help="Path to config file to use")
    prepare_db.add_argument("--dir", "--directory", action="store", help="Path of directory containing data")

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    setup_logging(args.verbose, args.logfile)

    args.function(args)
