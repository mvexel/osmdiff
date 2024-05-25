import logging

from osmdiff.settings import DEBUG

logger = logging.getLogger(__name__)


def get_logger(loglevel=logging.INFO):
    "Get a logger with the appropriate log level"
    if DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(loglevel)
    return logger
