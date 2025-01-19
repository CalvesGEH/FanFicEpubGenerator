import logging

from .config import get_config

config = get_config()

# This should only run once.

# Setup logging
logging.basicConfig(level=config.LOG_LEVEL, format='[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s] %(message)s')

# Our own getter to ensure that the config has been set.
def get_logger(name):
    return logging.getLogger(name)