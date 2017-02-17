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


class VolumeDoesNotExist(GpuCrateException):
    def __init__(self, vol):
        self.message = (
            'volume {vol} does not exist - run "gpucrate create"'.format(
                vol=vol)
        )
