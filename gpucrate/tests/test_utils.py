import sys

import mock
import testfixtures
from sh import which
from sh import realpath

from gpucrate import utils

NV_DRIVER_VERSION = '352.93'
PYNVML_MOCK = mock.MagicMock()
PYNVML_MOCK.nvmlSystemGetDriverVersion = mock.MagicMock(
    return_value=NV_DRIVER_VERSION)
PYNVML_MOCK.nvmlInit = mock.MagicMock(return_value=None)
IPY = mock.MagicMock()
IPY.embed = mock.MagicMock()
PUDB = mock.MagicMock()


@mock.patch.object(utils, 'pynvml', PYNVML_MOCK)
@mock.patch.object(PYNVML_MOCK, '_nvmlLib_refcount', 0)
def test_get_driver_version():
    def _side_effect():
        PYNVML_MOCK._nvmlLib_refcount += 1
    with mock.patch.object(PYNVML_MOCK.nvmlInit, 'side_effect', _side_effect):
        assert PYNVML_MOCK._nvmlLib_refcount == 0
        assert utils.get_driver_version() == NV_DRIVER_VERSION
        assert PYNVML_MOCK._nvmlLib_refcount == 1
        assert utils.get_driver_version() == NV_DRIVER_VERSION
        assert PYNVML_MOCK._nvmlLib_refcount == 1


def test_which():
    progs = ['ls', 'cd', 'which', 'cat', 'grep', 'find']
    for prog in progs:
        assert utils.which(prog) == realpath(which(prog)).stdout.strip()


@mock.patch.dict('sys.modules', IPython=IPY)
def test_with_ipython():
    IPY.embed.reset_mock()
    ns = dict(test=True)
    utils.shell(local_ns=ns)
    IPY.embed.assert_called_once_with(user_ns=ns)


@mock.patch.object(sys, 'path', [])
def test_without_ipython():
    with testfixtures.LogCapture() as log:
        utils.shell()
    log.check(
        ('gpucrate', 'ERROR',
         'Unable to load IPython:\n\nNo module named IPython\n'),
        ('gpucrate', 'ERROR',
         'Please check that IPython is installed and working.'),
    )


@mock.patch.dict('sys.modules', pudb=PUDB)
def test_with_pudb():
    pdb = utils.debugger()
    assert pdb == PUDB


@mock.patch.object(sys, 'path', [])
def test_without_pudb():
    pdb = utils.debugger()
    assert sys.modules.get('pdb') == pdb
