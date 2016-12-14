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


def test_get_libs():
    ldcache = ldconfig.parse_ldconfig_p(LDCACHE_DATA.splitlines()[1:])
    libs = ldconfig.get_libs(['libnvidia-tls'], ldcache=ldcache)
    libs64 = libs['lib64']
    libs32 = libs['lib32']
    assert len(libs32) == 0
    assert len(libs64) == 3
    for lib in libs64:
        assert lib['name'].startswith('libnvidia-tls')
        assert lib['elf'] == 'libc6,x86-64'
        if lib['hwcap']:
            assert lib['hwcap'] == '0x8000000000000000'
        assert lib['abi'].startswith('Linux 2.')
