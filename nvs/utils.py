import os

import distutils.spawn

import pynvml


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
