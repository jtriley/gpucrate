import logging
import logging.handlers


LOG_FORMAT = ("%(asctime)s %(filename)s:%(lineno)d - %(levelname)s - "
              "%(message)s")

log = logging.getLogger('gpucrate')
console = logging.StreamHandler()
formatter = logging.Formatter(LOG_FORMAT)
console.setFormatter(formatter)


def configure_gpucrate_logging(debug=False):
    """
    Configure logging for gpucrate *application* code

    By default gpucrate's logger is completely unconfigured so that other
    developers using gpucrate as a library can configure logging as they see
    fit.  This method is used in gpucrate's application code (i.e.  the
    'gpucrate' command) to toggle gpucrate's application specific
    formatters/handlers
    """
    log.setLevel(logging.DEBUG)
    if debug:
        console.setLevel(logging.DEBUG)
    else:
        console.setLevel(logging.INFO)
    log.addHandler(console)
