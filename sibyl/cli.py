import argparse

from sibyl.core import Sibyl
from sibyl.utils import read_config, setup_logging


def _run(sibyl, args):
    sibyl.run_server(args.env, args.port)


def get_parser():

    # Common Parent - Shared options
    common = argparse.ArgumentParser(add_help=False)

    common.add_argument('-l', '--logfile',
                        help='Name of the logfile.'
                             'If not given, log to stdout.')

    common.add_argument('-v', '--verbose', action='count', default=0,
                        help='Be verbose. Use -vv for increased verbosity.')

    common.add_argument('--docker', action='store_true',
                        help='deployed in docker environment')

    parser = argparse.ArgumentParser(
        description='sibyl Command Line Interface.')
    parser.set_defaults(function=None)

    # sibyl [action]
    action = parser.add_subparsers(title='action', dest='action')
    action.required = True

    # sibyl run
    run = action.add_parser('run', help='Start flask server', parents=[common])
    run.set_defaults(function=_run)

    run.add_argument('-P', '--port', type=int, help='Flask server port')
    run.add_argument('-E', '--env', type=str, help='Flask environment',
                     choices=['development', 'production', 'test'])

    return parser


def main():

    parser = get_parser()
    args = parser.parse_args()

    setup_logging(args.verbose, args.logfile)
    config = read_config('./sibyl/config.yml')
    sibyl = Sibyl(config, args.docker)

    args.function(sibyl, args)