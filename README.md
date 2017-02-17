# gpucrate

**NOTE**: This project should ideally go away once singularity gets built-in
support for this.

[![build status](https://secure.travis-ci.org/jtriley/gpucrate.png?branch=master)](https://secure.travis-ci.org/jtriley/gpucrate)

gpucrate creates hard-linked GPU driver (currently just NVIDIA) volumes for use
with docker, singularity, etc. This allows the exact system drivers to be
linked into a container without needing to maintain a separate container per
driver version.

## Installation
To install gpucrate use the `pip` command:

```
$ pip install gpucrate
```

or in a [virtual environment](https://virtualenv.pypa.io/en/stable/):

```
$ virtualenv gpucrate
$ source gpucrate/bin/activate
$ pip install gpucrate
```

## Usage
To create a driver volume for your system's current GPU driver:

```
$ sudo gpucrate create
```

This will create a hard-linked driver volume directory in `/usr/local/gpucrate`
by default that can be used to link the drivers into a container. Here's an
example volume for driver version `367.48`:

```
$ find /usr/local/gpucrate/367.48/
/usr/local/gpucrate/367.48/
/usr/local/gpucrate/367.48/bin
/usr/local/gpucrate/367.48/bin/nvidia-cuda-mps-server
/usr/local/gpucrate/367.48/bin/nvidia-debugdump
/usr/local/gpucrate/367.48/bin/nvidia-persistenced
/usr/local/gpucrate/367.48/bin/nvidia-cuda-mps-control
/usr/local/gpucrate/367.48/bin/nvidia-smi
/usr/local/gpucrate/367.48/lib
/usr/local/gpucrate/367.48/lib64
/usr/local/gpucrate/367.48/lib64/libnvcuvid.so.367.48
/usr/local/gpucrate/367.48/lib64/libnvidia-ml.so.1
/usr/local/gpucrate/367.48/lib64/libnvidia-eglcore.so.367.48
/usr/local/gpucrate/367.48/lib64/libnvidia-glcore.so.367.48
/usr/local/gpucrate/367.48/lib64/libcuda.so.367.48
/usr/local/gpucrate/367.48/lib64/libnvidia-opencl.so.1
/usr/local/gpucrate/367.48/lib64/libnvcuvid.so.1
/usr/local/gpucrate/367.48/lib64/libnvidia-ifr.so.367.48
/usr/local/gpucrate/367.48/lib64/libnvidia-ml.so.367.48
/usr/local/gpucrate/367.48/lib64/libcuda.so.1
/usr/local/gpucrate/367.48/lib64/libnvidia-encode.so.1
/usr/local/gpucrate/367.48/lib64/libnvidia-tls.so.367.48
/usr/local/gpucrate/367.48/lib64/libnvidia-egl-wayland.so.367.48
/usr/local/gpucrate/367.48/lib64/libOpenGL.so.0
/usr/local/gpucrate/367.48/lib64/libcuda.so
/usr/local/gpucrate/367.48/lib64/libnvidia-compiler.so.367.48
/usr/local/gpucrate/367.48/lib64/libnvidia-fatbinaryloader.so.367.48
/usr/local/gpucrate/367.48/lib64/libnvidia-opencl.so.367.48
/usr/local/gpucrate/367.48/lib64/libnvidia-ptxjitcompiler.so.367.48
/usr/local/gpucrate/367.48/lib64/libnvidia-fbc.so.1
/usr/local/gpucrate/367.48/lib64/libnvidia-fbc.so.367.48
/usr/local/gpucrate/367.48/lib64/libnvidia-glsi.so.367.48
/usr/local/gpucrate/367.48/lib64/libnvidia-encode.so.367.48
/usr/local/gpucrate/367.48/lib64/libnvidia-ifr.so.1
```

### Using with Singularity
Singularity utilizes a setuid script to properly configure the container at
runtime. Unfortunately this means we can't pass `$LD_LIBRARY_PATH` from outside
of the container because it's an unsecure variable which gets stripped by
glibc.

I have a [PR to singularity](https://github.com/singularityware/singularity/pull/424)
that enables securely passing these variables into the container's environment.
Until that gets merged we need to update the environment file inside of the
container if it doesn't already have `/usr/local/nvidia/{lib,lib64,bin}`
folders in `$LD_LIBRARY_PATH` and `$PATH`. You can update a singularity
container's environment file if necssary by running:

```
$ sudo gpucrate prepare container.img
```

Now we can run the container using the `singularity-gpu` wrapper installed by `gpucrate`:


```
$ singularity-gpu exec tensorflow.img python -c 'import tensorflow'
```

### Using with Docker
It's much easier to just use [nvidia-docker](https://github.com/NVIDIA/nvidia-docker).
If you still insist try this (not tested and you'll need to adjust the devices,
volume root, and driver version for your system):

```
$ docker run -ti --rm --device=/dev/nvidiactl --device=/dev/nvidia-uvm --device=/dev/nvidia3 --device=/dev/nvidia2 --device=/dev/nvidia1 --device=/dev/nvidia0 --volume-driver=nvidia-docker --volume=/usr/local/gpucrate/<driver_version>:/usr/local/nvidia:ro nvidia/cuda nvidia-smi
```

## Configuration
By default gpucrate creates driver volumes in `/usr/local/gpucrate`. You can
configure this several ways:

**via config**:
```
echo 'volume_root: /path/to/volume/root' > /etc/gpucrate/config
```

**via environment variable**:
```
export GPUCRATE_VOLUME_ROOT=/path/to/volume/root
```

