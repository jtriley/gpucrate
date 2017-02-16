import os
import yaml

from gpucrate.logger import log

_LOADED = False
_CONFIG = {
    'volume_root': '/usr/local/gpucrate',
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
