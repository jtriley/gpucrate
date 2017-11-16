# gpucrate

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

**NOTE**: singularity-gpu requires Singularity 2.4+

Once a volume has been created for the currently active driver you can now use
the singularity wrapper `singularity-gpu` to run GPU-enabled containers.

As an example lets convert the [tensorflow/tensorflow:latest-gpu](https://hub.docker.com/r/tensorflow/tensorflow/)
docker image to a singularity image:

```
$ singularity build tensorflow.img docker://tensorflow/tensorflow:latest-gpu

```

Now use the `singularity-gpu` wrapper to run any singularity command as normal
only with the host's exact GPU driver linked in:

```
$ singularity-gpu exec tensorflow.img python -c 'import tensorflow'
I tensorflow/stream_executor/dso_loader.cc:108] successfully opened CUDA library libcublas.so locally
I tensorflow/stream_executor/dso_loader.cc:108] successfully opened CUDA library libcudnn.so locally
I tensorflow/stream_executor/dso_loader.cc:108] successfully opened CUDA library libcufft.so locally
I tensorflow/stream_executor/dso_loader.cc:108] successfully opened CUDA library libcuda.so.1 locally
I tensorflow/stream_executor/dso_loader.cc:108] successfully opened CUDA library libcurand.so locally
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
configure this two ways:

**via config**:
```
echo 'volume_root: /path/to/volume/root' > /etc/gpucrate/config
```

**via environment variable**:
```
export GPUCRATE_VOLUME_ROOT=/path/to/volume/root
```
