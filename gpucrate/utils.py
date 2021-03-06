import os

import sh
import pynvml

from gpucrate.logger import log


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
    return os.path.realpath(sh.Command(prog)._path)


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


def debugger():
    """
    Drop to a debugger using pudb if available and pdb if not
    """
    try:
        import pudb as pdb
    except ImportError:
        import pdb
    return pdb
