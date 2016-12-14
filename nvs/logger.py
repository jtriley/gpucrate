import logging
import logging.handlers


LOG_FORMAT = ("%(asctime)s %(filename)s:%(lineno)d - %(levelname)s - "
              "%(message)s")

log = logging.getLogger('nvs')
console = logging.StreamHandler()
formatter = logging.Formatter(LOG_FORMAT)
console.setFormatter(formatter)


def configure_nvs_logging(debug=False):
    """
    Configure logging for nvs *application* code

    By default nvs's logger is completely unconfigured so that other
    developers using nvs as a library can configure logging as they see fit.
    This method is used in nvs's application code (i.e.  the 'nvs'
    command) to toggle nvs's application specific formatters/handlers
    """
    log.setLevel(logging.DEBUG)
    if debug:
        console.setLevel(logging.DEBUG)
    else:
        console.setLevel(logging.INFO)
    log.addHandler(console)
