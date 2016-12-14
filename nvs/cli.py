import argparse

from nvs import utils
from nvs import logger


def shell(args, **kwargs):
    ns = dict(log=logger.log)
    utils.shell(local_ns=ns)


def get_parser():
    parser = argparse.ArgumentParser(
        description='nvidia-singularity - NVIDIA support for Singularity')
    parser.add_argument('--debug', required=False,
                        action='store_true', default=False,
                        help='enable debug output')
    subparsers = parser.add_subparsers()
    shell_parser = subparsers.add_parser('shell')
    shell_parser.set_defaults(func=shell)
    return parser


def main(**kwargs):
    parser = get_parser()
    args = parser.parse_args(args=kwargs.pop('args', None))
    logger.configure_nvs_logging(debug=args.debug)
    args.func(args, **kwargs)
