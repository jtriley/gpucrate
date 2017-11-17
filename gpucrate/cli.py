import os
import sys
import argparse
import tempfile

import sh

from gpucrate import utils
from gpucrate import config
from gpucrate import logger
from gpucrate import volume
from gpucrate import exception
from gpucrate import __version__


NVENV = """
### START NVIDIA AND CUDA PATHS
PATH=$PATH:/usr/local/nvidia/bin:/usr/local/cuda/bin
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/nvidia/lib
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/nvidia/lib64
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib/:/usr/local/cuda/lib64/
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/extras/CUPTI/lib64/
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64/include/
LIBRARY_PATH="$LIBRARY_PATH:/usr/local/cuda/lib64/stubs"
CUDA_HOME=/usr/local/cuda
export PATH LD_LIBRARY_PATH LIBRARY_PATH CUDA_HOME
### END NVIDIA AND CUDA PATHS
"""


def shell(**kwargs):
    ns = dict(log=logger.log)
    utils.shell(local_ns=ns)


def create(**kwargs):
    volume_root = config.get_volume_root()
    if os.geteuid() != 0:
        raise exception.RootRequired
    if not os.path.isdir(volume_root):
        logger.log.info(
            "Volume root {volume_root} does not exist - creating".format(
                volume_root=volume_root))
        os.makedirs(volume_root)
    vols = volume.lookup_volumes()
    for vol in vols:
        volume.create(volume_root, vols[vol])


def get_gpucrate_parser():
    parser = argparse.ArgumentParser(
        prog='gpucrate',
        description='creates GPU driver volumes for containers')
    parser.add_argument('--debug', required=False,
                        action='store_true', default=False,
                        help='enable debug output')
    parser.add_argument('--version', action='version', version=__version__)
    subparsers = parser.add_subparsers()
    create_parser = subparsers.add_parser('create')
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


def gpu_wrap_singularity(env_file):
    driver_version = utils.get_driver_version()
    volume_root = config.get_volume_root()
    vol = os.path.join(volume_root, driver_version)
    if not os.path.isdir(vol):
        raise exception.VolumeDoesNotExist(vol)
    bind_paths = []
    singularity = sh.Command('singularity')
    env_file.write(NVENV)
    env_file.flush()
    bind_paths.append("{vol}:/usr/local/nvidia".format(vol=vol))
    bind_paths.append(
        "{env}:/.singularity.d/env/99-gpucrate.sh".format(env=env_file.name))
    env = os.environ.copy()
    if bind_paths:
        env['SINGULARITY_BINDPATH'] = ','.join(bind_paths)
    singularity(*sys.argv[1:], _env=env, _fg=True)


def singularity_gpu(**kwargs):
    logger.configure_gpucrate_logging()
    try:
        with tempfile.NamedTemporaryFile() as f:
            gpu_wrap_singularity(f)
    except exception.GpuCrateException as e:
        logger.log.error(e.message)
        exit(1)
    except sh.ErrorReturnCode as e:
        exit(e.exit_code)
