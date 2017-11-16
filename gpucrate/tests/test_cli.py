import os
import sys

import sh
import mock
import pytest
import testfixtures

from gpucrate import cli
from gpucrate import utils
from gpucrate import config
from gpucrate import exception


ROOT = mock.MagicMock(return_value=0)
NON_ROOT = mock.MagicMock(return_value=1)
PDB = mock.MagicMock()
PDB.set_trace = mock.MagicMock(side_effect=sys.exit)
SHELL = mock.MagicMock()
FAKE_ERROR_RETURN_CODE = sh.ErrorReturnCode('fake_cmd', '', '')
FAKE_ERROR_RETURN_CODE.exit_code = 777
FAKE_RESULT = mock.MagicMock()
FAKE_RESULT.stdout = 'FAKE_ENV=test'
SINGULARITY = mock.MagicMock(return_value=FAKE_RESULT)
TEST_DRIVER_VERSION = '367.48'
GPU_WRAP_SINGULARITY = mock.MagicMock()


def test_help():
    with pytest.raises(SystemExit):
        cli.main(args=['--help'])


@mock.patch.object(cli.utils, 'shell', SHELL)
@mock.patch.object(cli, 'logger', mock.MagicMock())
def test_shell():
    SHELL.reset_mock()
    cli.main(args=['shell'], test=True)
    SHELL.assert_called_once_with(local_ns=dict(log=cli.logger.log))


@mock.patch.object(utils, 'debugger', mock.MagicMock(return_value=PDB))
def test_debug():
    PDB.set_trace.reset_mock()
    with pytest.raises(SystemExit):
        cli.main(args=['--debug', 'create'])
    PDB.set_trace.assert_called_once()


@mock.patch.dict('os.environ', PATH='')
def _load_non_existent_sh_cmd(*args, **kwargs):
    sh.Command("doesnotexist")


@mock.patch.object(cli, 'create', _load_non_existent_sh_cmd)
def test_shell_cmd_not_found():
    with pytest.raises(SystemExit) as excinfo:
        with testfixtures.LogCapture() as log_capture:
            cli.main(args=['create'])
    log_capture.check(
        ('gpucrate',
         'ERROR',
         'required command not found: doesnotexist'),
    )
    assert excinfo.value.code == 2


def _raise_gpucrate_error(*args, **kwargs):
    raise exception.GpuCrateException('gpucrate error')


@mock.patch.object(cli, 'create', _raise_gpucrate_error)
def test_gpu_crate_error():
    with pytest.raises(SystemExit) as excinfo:
        with testfixtures.LogCapture() as log_capture:
            cli.main(args=["create"])
    log_capture.check(
        ('gpucrate',
         'ERROR',
         'gpucrate error')
    )
    assert excinfo.value.code == 1


@mock.patch.object(config, '_CONFIG', config._CONFIG.copy())
def test_create_no_volume_root():
    with pytest.raises(SystemExit):
        with testfixtures.LogCapture() as log_capture:
            with testfixtures.TempDirectory() as d:
                d.write('config', 'volume_root:')
                config.load(path=os.path.join(d.path, 'config'))
                cli.main(args=['create'])
    log_capture.check(
        ('gpucrate',
         'ERROR',
         exception.NoVolumeRoot.message),
    )


@mock.patch.object(os, 'geteuid', NON_ROOT)
def test_create_root_required():
    with pytest.raises(SystemExit):
        with testfixtures.LogCapture() as log_capture:
            cli.main(args=['create'])
    log_capture.check(
        ('gpucrate',
         'ERROR',
         exception.RootRequired.message),
    )


@mock.patch.object(os, 'geteuid', ROOT)
@mock.patch.object(config, '_CONFIG', config._CONFIG.copy())
@mock.patch.object(cli.volume, 'lookup_volumes',
                   mock.MagicMock(return_value={'fake': {}}))
@mock.patch.object(cli.volume, 'create',
                   mock.MagicMock())
def test_create_volume_root_dne():
    with testfixtures.LogCapture() as log_capture:
        with testfixtures.TempDirectory() as d:
            vroot = os.path.join(d.path, 'vroot')
            d.write('config', 'volume_root: {vroot}'.format(vroot=vroot))
            config.load(path=os.path.join(d.path, 'config'))
            cli.main(args=['create'])
            assert os.path.isdir(vroot)
    log_capture.check(
        ('gpucrate',
         'INFO',
         'Volume root {vroot} does not exist - creating'.format(vroot=vroot))
    )


@mock.patch.object(os.path, 'isdir', mock.MagicMock(return_value=True))
@mock.patch.object(cli.utils, 'get_driver_version',
                   mock.MagicMock(return_value=TEST_DRIVER_VERSION))
@mock.patch.object(sh, 'Command', mock.MagicMock(return_value=SINGULARITY))
def test_singularity_gpu_success():
    SINGULARITY.reset_mock()
    kwargs = dict(args='exec -B /some/path:/some/path c.img'.split())
    cli.singularity_gpu(**kwargs)
    assert SINGULARITY.call_count == 1


@mock.patch.object(os.path, 'isdir', mock.MagicMock(return_value=True))
@mock.patch.object(cli.utils, 'get_driver_version',
                   mock.MagicMock(return_value=TEST_DRIVER_VERSION))
@mock.patch.object(sh, 'Command', mock.MagicMock(return_value=SINGULARITY))
def test_singularity_gpu_failure():
    SINGULARITY.reset_mock()
    kwargs = dict(args='exec -B /some/path:/some/path c.img'.split())
    cli.singularity_gpu(**kwargs)
    assert SINGULARITY.call_count == 1


@mock.patch.object(cli.utils, 'get_driver_version',
                   mock.MagicMock(return_value=TEST_DRIVER_VERSION))
@mock.patch.object(sh, 'Command', mock.MagicMock(return_value=SINGULARITY))
def test_singularity_gpu_volume_dne():
    with pytest.raises(SystemExit):
        with testfixtures.LogCapture() as log_capture:
            with testfixtures.TempDirectory() as d:
                vroot = os.path.join(d.path, 'vroot')
                vol = os.path.join(vroot, TEST_DRIVER_VERSION)
                d.write('config', 'volume_root: {vroot}'.format(vroot=vroot))
                config.load(path=os.path.join(d.path, 'config'))
                SINGULARITY.reset_mock()
                cli.singularity_gpu(
                    args='exec -B /some/path:/some/path c.img'.split())

    log_capture.check(
        ('gpucrate',
         'ERROR',
         'volume {vol} does not exist - run "gpucrate create"'.format(vol=vol))
    )


@mock.patch.object(sh, 'Command', mock.MagicMock(return_value=SINGULARITY))
@mock.patch.object(os.path, 'isdir', mock.MagicMock(return_value=True))
@mock.patch.object(cli.utils, 'get_driver_version',
                   mock.MagicMock(return_value=TEST_DRIVER_VERSION))
def test_singularity_gpu_fail():
    with mock.patch.object(SINGULARITY, 'side_effect', FAKE_ERROR_RETURN_CODE):
        with pytest.raises(SystemExit) as excinfo:
            SINGULARITY.reset_mock()
            GPU_WRAP_SINGULARITY.reset_mock()
            kwargs = dict(args='exec -B /path:/path c.img'.split())
            cli.singularity_gpu(**kwargs)
    assert excinfo.value.code == FAKE_ERROR_RETURN_CODE.exit_code
