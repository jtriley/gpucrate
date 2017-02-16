import os
import argparse

import sh

from gpucrate import utils
from gpucrate import config
from gpucrate import logger
from gpucrate import volume
from gpucrate import exception


def shell(**kwargs):
    ns = dict(log=logger.log)
    utils.shell(local_ns=ns)


def get_gpucrate_parser():
    parser = argparse.ArgumentParser(
        prog='gpucrate',
        description='creates GPU driver volumes for containers')
    parser.add_argument('--debug', required=False,
                        action='store_true', default=False,
                        help='enable debug output')
    subparsers = parser.add_subparsers()
    create_parser = subparsers.add_parser('create')
    create_parser.add_argument(
        '--volume-root', required=False,
        help='path where GPU driver volumes are created'
    )
    create_parser.set_defaults(func=create)
    shell_parser = subparsers.add_parser('shell')
    shell_parser.set_defaults(func=shell)
    return parser


def main(**kwargs):
    parser = get_gpucrate_parser()
    args = parser.parse_args(args=kwargs.pop('args', None))
    args_dict = vars(args)
    debug = args_dict.pop('debug')
    logger.configure_gpucrate_logging(debug=debug)
    if debug:
        pdb = utils.debugger()
        pdb.set_trace()
    try:
        args.func(**args_dict)
    except sh.CommandNotFound as e:
        logger.log.error("required command not found: {e}".format(e=e))
        exit(2)
    except exception.GpuCrateException as e:
        logger.log.error(e.message)
        exit(1)


def create(volume_root=None, **kwargs):
    volume_root = (volume_root or os.environ.get('GPUCRATE_VOLUME_ROOT') or
                   config.get('volume_root'))
    if not volume_root:
        raise exception.NoVolumeRoot
    if os.geteuid() != 0:
        raise exception.RootRequired
    if not os.path.isdir(volume_root):
        logger.log.info("Volume root {volume_root} does not exist".format(
            volume_root=volume_root))
        os.makedirs(volume_root)
    vols = volume.lookup_volumes()
    for vol in vols:
        volume.create(volume_root, vols)
