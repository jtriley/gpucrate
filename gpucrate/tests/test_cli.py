import pytest

import mock

from gpucrate import cli


SHELL = mock.MagicMock()


def test_cli_help():
    with pytest.raises(SystemExit):
        cli.main(args=['--help'])


@mock.patch.object(cli.utils, 'shell', SHELL)
@mock.patch.object(cli, 'logger', mock.MagicMock())
def test_shell():
    SHELL.reset_mock()
    cli.main(args=['shell'], test=True)
    SHELL.assert_called_once_with(local_ns=dict(log=cli.logger.log))
