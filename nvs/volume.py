import os
import re

from sh import ld

from nvs import utils
from nvs import ldconfig


VOLUMES = [
    {
        "name": "nvidia_driver",
        "path": "/usr/local/nvidia",
        "binaries": {
            #"nvidia-modprobe",        # Kernel module loader
            #"nvidia-settings",        # X server settings
            #"nvidia-xconfig",         # X xorg.conf editor
            "nvidia-cuda-mps-control", # Multi process service CLI
            "nvidia-cuda-mps-server",  # Multi process service server
            "nvidia-debugdump",        # GPU coredump utility
            "nvidia-persistenced",     # Persistence mode utility
            "nvidia-smi",              # System management interface
        },
        "libraries": {
            # ------- X11 -------

            #"libnvidia-cfg.so",  # GPU configuration (used by nvidia-xconfig)
            #"libnvidia-gtk2.so", # GTK2 (used by nvidia-settings)
            #"libnvidia-gtk3.so", # GTK3 (used by nvidia-settings)
            #"libnvidia-wfb.so",  # Wrapped software rendering module for X server
            #"libglx.so",         # GLX extension module for X server

            # ----- Compute -----

            "libnvidia-ml.so",              # Management library
            "libcuda.so",                   # CUDA driver library
            "libnvidia-ptxjitcompiler.so",  # PTX-SASS JIT compiler (used by libcuda)
            "libnvidia-fatbinaryloader.so", # fatbin loader (used by libcuda)
            "libnvidia-opencl.so",          # NVIDIA OpenCL ICD
            "libnvidia-compiler.so",        # NVVM-PTX compiler for OpenCL (used by libnvidia-opencl)
            #"libOpenCL.so",                # OpenCL ICD loader

            # ------ Video ------

            "libvdpau_nvidia.so",  # NVIDIA VDPAU ICD
            "libnvidia-encode.so", # Video encoder
            "libnvcuvid.so",       # Video decoder
            "libnvidia-fbc.so",    # Framebuffer capture
            "libnvidia-ifr.so",    # OpenGL framebuffer capture

            # ----- Graphic -----

            # XXX In an ideal world we would only mount nvidia_* vendor specific libraries and
            # install ICD loaders inside the container. However, for backward compatibility reason
            # we need to mount everything. This will hopefully change once GLVND is well established.

            "libGL.so",         # OpenGL/GLX legacy _or_ compatibility wrapper (GLVND)
            "libGLX.so",        # GLX ICD loader (GLVND)
            "libOpenGL.so",     # OpenGL ICD loader (GLVND)
            "libGLESv1_CM.so",  # OpenGL ES v1 common profile legacy _or_ ICD loader (GLVND)
            "libGLESv2.so",     # OpenGL ES v2 legacy _or_ ICD loader (GLVND)
            "libEGL.so",        # EGL ICD loader
            "libGLdispatch.so", # OpenGL dispatch (GLVND) (used by libOpenGL, libEGL and libGLES*)

            "libGLX_nvidia.so",         # OpenGL/GLX ICD (GLVND)
            "libEGL_nvidia.so",         # EGL ICD (GLVND)
            "libGLESv2_nvidia.so",      # OpenGL ES v2 ICD (GLVND)
            "libGLESv1_CM_nvidia.so",   # OpenGL ES v1 common profile ICD (GLVND)
            "libnvidia-eglcore.so",     # EGL core (used by libGLES* or libGLES*_nvidia and libEGL_nvidia)
            "libnvidia-egl-wayland.so", # EGL wayland extensions (used by libEGL_nvidia)
            "libnvidia-glcore.so",      # OpenGL core (used by libGL or libGLX_nvidia)
            "libnvidia-tls.so",         # Thread local storage (used by libGL or libGLX_nvidia)
            "libnvidia-glsi.so",        # OpenGL system interaction (used by libEGL_nvidia)
        },
    }
]


def blacklisted(f, abi):
    lib = re.compile('^.*/lib([\w-]+)\.so[\d.]*$')
    glcore = re.compile('libnvidia-e?glcore\.so')
    gldispatch = re.compile('libGLdispatch\.so')
    m = lib.match(f)
    if not m:
        return True
    name = m.groups()[0]
    if name in ['EGL', 'GLESv1_CM', 'GLESv2', 'GL']:
        deps = ldconfig.ldd(f)
        for d in deps:
            if glcore.match(d) or gldispatch.match(d):
                return False
        return True
    # Blacklist TLS libraries using the old ABI (!= 2.3.99)
    if name == "nvidia-tls":
        abi_target = '2.3.99'
        return abi.split()[-1] != abi_target
    return False


def lookup_volumes():
    """
    Returns list of volumes to be created for current driver
    """
    drv = utils.get_driver_version()
    vols = {}
    for v in VOLUMES:
        name = v['name']
        vol = dict(version=drv)
        binaries = v.get('binaries')
        libraries = v.get('libraries')
        if binaries:
            bins = [utils.which(binary) for binary in binaries]
            vol['binaries'] = bins
        if libraries:
            vol['libraries'] = ldconfig.get_libs(libraries)
        vols[name] = vol
    return vols
