import os

import distutils.spawn

import pynvml
pynvml.nvmlInit()


def get_driver_version():
    """
    Return current NVIDIA driver version
    """
    return pynvml.nvmlSystemGetDriverVersion()


def which(prog):
    """
    Returns realpath of program
    """
    return os.path.realpath(distutils.spawn.find_executable(prog))
