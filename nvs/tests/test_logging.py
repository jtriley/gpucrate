import logging

from testfixtures import LogCapture

from nvs import logger


def test_nvs_logger():
    assert not logger.log.handlers
    with LogCapture() as log_capture:
        logger.configure_nvs_logging()
        assert logger.log.handlers
        assert logger.console.level == logging.INFO
        logger.log.info('test')
        logger.configure_nvs_logging(debug=True)
        assert logger.console.level == logging.DEBUG
        logger.log.debug('test')
    log_capture.check(
        ('nvs', 'INFO', 'test'),
        ('nvs', 'DEBUG', 'test'),
    )
