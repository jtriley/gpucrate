import mock

from nvs import ldconfig
from nvs.tests import utils

SH_MOCK = mock.MagicMock()
SH_MOCK_RESULT = mock.MagicMock()
SH_MOCK_INST = mock.MagicMock(return_value=SH_MOCK_RESULT)
SH_MOCK_CMD = mock.MagicMock(return_value=SH_MOCK_INST)
SH_MOCK.Command = SH_MOCK_CMD
SH_MODULES = dict(sh=SH_MOCK)

LDCACHE_DATA = utils.get_test_data('ldcache.txt')


@mock.patch.object(ldconfig, 'sh', SH_MOCK)
@mock.patch.object(SH_MOCK_RESULT, 'stdout', LDCACHE_DATA)
def test_ldcache():
    ldcache = ldconfig.get_ldconfig_cache()
    assert len(ldcache) == len(LDCACHE_DATA.splitlines()) - 1  # minus header
