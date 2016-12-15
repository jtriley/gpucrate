import os

import distutils.spawn

import pynvml

from nvs.logger import log


def get_driver_version():
    """
    Return current NVIDIA driver version
    """
    if not pynvml._nvmlLib_refcount:
        pynvml.nvmlInit()
    return pynvml.nvmlSystemGetDriverVersion()


def which(prog):
    """
    Returns realpath of program
    """
    return os.path.realpath(distutils.spawn.find_executable(prog))


def shell(local_ns={}):
    """
    Launches an embedded IPython shell
    """
    try:
        from IPython import embed
        return embed(user_ns=local_ns)
    except ImportError as e:
        log.error("Unable to load IPython:\n\n%s\n" % e)
        log.error("Please check that IPython is installed and working.")
