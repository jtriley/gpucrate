import os
import yaml

from gpucrate import exception
from gpucrate.logger import log

_LOADED = False
_CONFIG = {
    'volume_root': '/usr/local/gpucrate',
    'manage_environment': True,
}
_TRUTH = {
    '1': True,
    '0': False,
    'true': True,
    'false': False,
}
DEFAULT_CONFIG_PATH = '/etc/gpucrate/config.yaml'


def load(path=DEFAULT_CONFIG_PATH):
    if not os.path.isfile(path):
        log.warn("Config not found: {cfg} - using internal defaults".format(
            cfg=path))
    else:
        with open(path) as f:
            globals()['_CONFIG'].update(yaml.load(f) or {})
    globals()['_LOADED'] = True


def get(key, path=DEFAULT_CONFIG_PATH):
    if not _LOADED:
        load(path=path)
    return _CONFIG.get(key)


def get_volume_root():
    vroot = os.environ.get('GPUCRATE_VOLUME_ROOT') or get('volume_root')
    if not vroot:
        raise exception.NoVolumeRoot
    return vroot


def get_manage_env():
    env_value = os.environ.get('GPUCRATE_MANAGE_ENVIRONMENT', None)
    if env_value is not None:
        return _TRUTH.get(env_value, False)
    else:
        return get('manage_environment')
