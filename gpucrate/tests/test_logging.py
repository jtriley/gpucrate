import logging

import mock
from testfixtures import LogCapture

from gpucrate import logger


@mock.patch.object(logger.log, 'handlers', [])
def test_gpucrate_logger():
    assert not logger.log.handlers
    with LogCapture() as log_capture:
        logger.configure_gpucrate_logging()
        assert logger.log.handlers
        assert logger.console.level == logging.INFO
        logger.log.info('test')
        logger.configure_gpucrate_logging(debug=True)
        assert logger.console.level == logging.DEBUG
        logger.log.debug('test')
    log_capture.check(
        ('gpucrate', 'INFO', 'test'),
        ('gpucrate', 'DEBUG', 'test'),
    )
