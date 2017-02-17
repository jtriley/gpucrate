class GpuCrateException(Exception):
    pass


class NoVolumeRoot(GpuCrateException):
    message = """\
No volume root defined! Please specify the volume root in the environment \
(export GPUCRATE_VOLUME_ROOT=/path), or in /etc/gpucrate/config \
(volume_root: /path)\
"""


class RootRequired(GpuCrateException):
    message = 'create command requires root privileges'
