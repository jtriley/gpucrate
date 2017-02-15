import os

import mock
import testfixtures

from gpucrate import config


def isfile_false(*args, **kwargs):
    return False


@mock.patch.object(config, '_LOADED', False)
@mock.patch.object(config, '_CONFIG', config._CONFIG.copy())
@mock.patch.object(os.path, 'isfile', isfile_false)
def test_no_config_file():
    with testfixtures.LogCapture() as log_capture:
        config.load()
    log_capture.check(
        ('gpucrate', 'WARNING', "Config not found: {cfg} - using internal "
         "defaults".format(cfg=config.DEFAULT_CONFIG_PATH))
    )


@mock.patch.object(config, '_LOADED', False)
@mock.patch.object(config, '_CONFIG', config._CONFIG.copy())
def test_with_config_file():
    with testfixtures.TempDirectory() as d:
        vroot = '/path/to/some/gpucrate/root'
        d.write('config', 'volume_root: {vroot}'.format(vroot=vroot))
        config.load(path=os.path.join(d.path, 'config'))
        assert config.get('volume_root') == vroot


@mock.patch.object(config, '_LOADED', False)
@mock.patch.object(config, '_CONFIG', config._CONFIG.copy())
def test_unloaded():
    assert config._LOADED is False
    config.get('volume_root')
    assert config._LOADED is True
