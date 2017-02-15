import os
import re

from gpucrate import utils
from gpucrate import ldconfig
from gpucrate import readelf


BIN_DIR = 'bin'
LIB32_DIR = 'lib'
LIB64_DIR = 'lib64'

VOLUMES = [
    {
        "name": "nvidia_driver",
        "path": "/usr/local/nvidia",
        "binaries": {
            # "nvidia-modprobe",        # Kernel module loader
            # "nvidia-settings",        # X server settings
            # "nvidia-xconfig",         # X xorg.conf editor
            "nvidia-cuda-mps-control",  # Multi process service CLI
            "nvidia-cuda-mps-server",   # Multi process service server
            "nvidia-debugdump",         # GPU coredump utility
            "nvidia-persistenced",      # Persistence mode utility
            "nvidia-smi",               # System management interface
        },
        "libraries": {
            # ------- X11 -------

            # "libnvidia-cfg.so",  # GPU configuration (used by nvidia-xconfig)
            # "libnvidia-gtk2.so", # GTK2 (used by nvidia-settings)
            # "libnvidia-gtk3.so", # GTK3 (used by nvidia-settings)
            # "libnvidia-wfb.so",  # Wrapped software rendering module for X server # noqa: E501
            # "libglx.so",         # GLX extension module for X server

            # ----- Compute -----

            "libnvidia-ml.so",               # Management library
            "libcuda.so",                    # CUDA driver library
            "libnvidia-ptxjitcompiler.so",   # PTX-SASS JIT compiler (used by libcuda) # noqa: E501
            "libnvidia-fatbinaryloader.so",  # fatbin loader (used by libcuda)
            "libnvidia-opencl.so",           # NVIDIA OpenCL ICD
            "libnvidia-compiler.so",         # NVVM-PTX compiler for OpenCL (used by libnvidia-opencl) # noqa: E501
            # "libOpenCL.so",                # OpenCL ICD loader

            # ------ Video ------

            "libvdpau_nvidia.so",   # NVIDIA VDPAU ICD
            "libnvidia-encode.so",  # Video encoder
            "libnvcuvid.so",        # Video decoder
            "libnvidia-fbc.so",     # Framebuffer capture
            "libnvidia-ifr.so",     # OpenGL framebuffer capture

            # ----- Graphic -----

            # XXX In an ideal world we would only mount nvidia_* vendor
            # specific libraries and install ICD loaders inside the container.
            # However, for backward compatibility reason we need to mount
            # everything. This will hopefully change once GLVND is well
            # established.

            "libGL.so",          # OpenGL/GLX legacy _or_ compatibility wrapper (GLVND) # noqa: E501
            "libGLX.so",         # GLX ICD loader (GLVND)
            "libOpenGL.so",      # OpenGL ICD loader (GLVND)
            "libGLESv1_CM.so",   # OpenGL ES v1 common profile legacy _or_ ICD loader (GLVND) # noqa: E501
            "libGLESv2.so",      # OpenGL ES v2 legacy _or_ ICD loader (GLVND)
            "libEGL.so",         # EGL ICD loader
            "libGLdispatch.so",  # OpenGL dispatch (GLVND) (used by libOpenGL, libEGL and libGLES*) # noqa: E501

            "libGLX_nvidia.so",          # OpenGL/GLX ICD (GLVND)
            "libEGL_nvidia.so",          # EGL ICD (GLVND)
            "libGLESv2_nvidia.so",       # OpenGL ES v2 ICD (GLVND)
            "libGLESv1_CM_nvidia.so",    # OpenGL ES v1 common profile ICD (GLVND) # noqa: E501
            "libnvidia-eglcore.so",      # EGL core (used by libGLES* or libGLES*_nvidia and libEGL_nvidia) # noqa: E501
            "libnvidia-egl-wayland.so",  # EGL wayland extensions (used by libEGL_nvidia) # noqa: E501
            "libnvidia-glcore.so",       # OpenGL core (used by libGL or libGLX_nvidia) # noqa: E501
            "libnvidia-tls.so",          # Thread local storage (used by libGL or libGLX_nvidia) # noqa: E501
            "libnvidia-glsi.so",         # OpenGL system interaction (used by libEGL_nvidia) # noqa: E501
        },
    }
]


def blacklisted(f, abi):
    """
    Returns True/False based on whether the library has been blacklisted or not
    """
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
            libs = ldconfig.get_libs(libraries, follow_links=True)
            lib32 = [i for i in libs['lib32']
                     if not blacklisted(i['path'], i['abi'])]
            lib64 = [i for i in libs['lib64']
                     if not blacklisted(i['path'], i['abi'])]
            libs['lib32'] = lib32
            libs['lib64'] = lib64
            vol['libraries'] = libs
        vols[name] = vol
    return vols


def create(path, volume):
    """
    Create
    """
    version = volume['version']
    root = os.path.join(path, version)
    bin_dir = os.path.join(root, BIN_DIR)
    lib32_dir = os.path.join(root, LIB32_DIR)
    lib64_dir = os.path.join(root, LIB64_DIR)
    for d in [bin_dir, lib32_dir, lib64_dir]:
        os.makedirs(d, 0755)
    binaries = volume['binaries']
    libraries = volume['libraries']
    lib32 = libraries['lib32']
    lib64 = libraries['lib64']
    for exe in binaries:
        os.link(exe, os.path.join(bin_dir, os.path.basename(exe)))
    for libs, dest_dir in [(lib32, lib32_dir), (lib64, lib64_dir)]:
        for lib in libs:
            path = lib['path']
            basename = os.path.basename(path)
            hardlink_dest = os.path.join(dest_dir, basename)
            if not os.path.isfile(hardlink_dest):
                os.link(path, hardlink_dest)
            soname = readelf.get_soname(path)
            if soname and soname != basename:
                solink = os.path.join(dest_dir, soname)
                if not os.path.islink(solink):
                    os.symlink(basename, solink)
            if soname:
                if basename.split('.')[0] == 'libcuda':
                    cuda_link = os.path.join(dest_dir, 'libcuda.so')
                    if not os.path.islink(cuda_link):
                        os.symlink(basename, cuda_link)
                if basename.split('.')[0] == 'libGLX_nvidia':
                    glx_link = os.path.join(dest_dir, basename.replace(
                        'GLX_nvidia', 'GLX_indirect'))
                    if not os.path.islink(glx_link):
                        os.symlink(basename, glx_link)
