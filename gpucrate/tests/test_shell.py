import sys

import mock

from testfixtures import LogCapture

IPY = mock.MagicMock()
IPY.embed = mock.MagicMock()

IPY_MODULES = {
    'IPython': IPY,
}


@mock.patch.dict('sys.modules', IPY_MODULES)
def test_with_ipython():
    IPY.embed.reset_mock()
    from gpucrate import utils
    ns = dict(test=True)
    utils.shell(local_ns=ns)
    IPY.embed.assert_called_once_with(user_ns=ns)


@mock.patch.object(sys, 'path', [])
def test_without_ipython():
    from gpucrate import utils
    with LogCapture() as log:
        utils.shell()
    log.check(
        ('gpucrate', 'ERROR',
         'Unable to load IPython:\n\nNo module named IPython\n'),
        ('gpucrate', 'ERROR',
         'Please check that IPython is installed and working.'),
    )
