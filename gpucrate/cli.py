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


NVENV = """
### START NVIDIA AND CUDA PATHS
PATH=$PATH:/usr/local/nvidia/bin:/usr/local/cuda/bin
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/nvidia/lib
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/nvidia/lib64
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib/:/usr/local/cuda/lib64/
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/extras/CUPTI/lib64/
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64/include/
CUDA_HOME=/usr/local/cuda
export PATH LD_LIBRARY_PATH CUDA_HOME
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


def add_common_args(parser):
    parser.add_argument('-B', '--bind', action="append")
    parser.add_argument('-c', '--contain', action='store_true')
    parser.add_argument('-C', '--containall', action='store_true')
    parser.add_argument('-H', '--home')
    parser.add_argument('-i', '--ipc', action='store_true')
    parser.add_argument('-p', '--pid', action='store_true')
    parser.add_argument('--pwd', action='store_true')
    parser.add_argument('-S', '--scratch')
    parser.add_argument('-u', '--user', action='store_true')
    parser.add_argument('-W', '--workdir')
    parser.add_argument('-w', '--writable', action='store_true')


def get_singularity_gpu_parser():
    parser = utils.SilentParser()
    parser.add_argument('-d', '--debug')
    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser('run')
    add_common_args(run_parser)
    run_parser.add_argument('container')
    run_parser.add_argument('vargs', nargs='*')

    exec_parser = subparsers.add_parser('exec')
    add_common_args(exec_parser)
    exec_parser.add_argument('container')
    exec_parser.add_argument('vargs', nargs='*')

    shell_parser = subparsers.add_parser('shell')
    add_common_args(shell_parser)
    shell_parser.add_argument('container')

    test_parser = subparsers.add_parser('test')
    test_parser.add_argument('container')

    return parser


def gpu_wrap_singularity(container, env_file, singularity=None):
    bind_paths = []
    container_env = None
    singularity = singularity or sh.Command('singularity')
    bind_paths = bind_paths or []
    if container:
        driver_version = utils.get_driver_version()
        volume_root = config.get_volume_root()
        vol = os.path.join(volume_root, driver_version)
        if not os.path.isdir(vol):
            raise exception.VolumeDoesNotExist(vol)
        container_env = singularity("exec {container} cat /environment".format(
            container=container).split()).stdout
        container_env += NVENV
        env_file.write(container_env)
        env_file.flush()
        bind_paths.append("{vol}:/usr/local/nvidia".format(vol=vol))
        bind_paths.append("{env}:/environment".format(env=env_file.name))

    env = os.environ.copy()
    if bind_paths:
        env['SINGULARITY_BINDPATH'] = ','.join(bind_paths)
    singularity(*sys.argv[1:], _env=env, _fg=True)


def singularity_gpu(**kwargs):
    logger.configure_gpucrate_logging()
    singularity = sh.Command('singularity')
    parser = get_singularity_gpu_parser()
    container = None

    try:
        args = parser.parse_args(args=kwargs.pop('args', None))
        container = args.container
    except SystemExit:
        pass

    try:
        with tempfile.NamedTemporaryFile() as f:
            gpu_wrap_singularity(container, f, singularity=singularity)
    except exception.GpuCrateException as e:
        logger.log.error(e.message)
        exit(1)
    except sh.ErrorReturnCode as e:
        exit(e.exit_code)
