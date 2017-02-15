import mock

from gpucrate import readelf
from gpucrate.tests import utils

SH_MOCK = mock.MagicMock()
SH_MOCK_RESULT = mock.MagicMock()
SH_MOCK_INST = mock.MagicMock(return_value=SH_MOCK_RESULT)
SH_MOCK_CMD = mock.MagicMock(return_value=SH_MOCK_INST)
SH_MOCK.Command = SH_MOCK_CMD

READELF_DATA = utils.get_test_data('readelf.txt')


@mock.patch.object(readelf, 'sh', SH_MOCK)
@mock.patch.object(SH_MOCK_RESULT, 'stdout', READELF_DATA)
def test_get_soname():
    soname = readelf.get_soname('/usr/lib64/nvidia/libcuda.so.352.93')
    assert soname == 'libcuda.so.1'
