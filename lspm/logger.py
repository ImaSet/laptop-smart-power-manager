# -*- coding: utf-8 -*-

"""
LSPM Logging System
*******************

This module defines the root logger used in some modules of the package.
"""

# ---------------------------------------- IMPORTS ----------------------------------------

from logging import getLogger, Filter, Formatter
from logging.handlers import RotatingFileHandler
from pathlib import Path

from lspm.parameters import LOGGING_LEVEL


# ---------------------------------------- CLASSES ----------------------------------------

class LSPMLoggingFilter(Filter):

    def filter(self, record):
        return record.name == 'lspm'


# ---------------------------------------- METHODS ----------------------------------------


def set_logging() -> None:
    """
    TODO

    :return: None
    """
    # Create Smart Plug config directory if it doesn't exist
    lspm_config_dir = Path(Path.home(), '.lspm')
    if not lspm_config_dir.exists():
        lspm_config_dir.mkdir()

    # Prepare LSPM root logger
    handler = RotatingFileHandler(Path(lspm_config_dir, 'app.log'), maxBytes=10000, backupCount=1)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)8s - %(message)s')
    handler.setFormatter(formatter)
    handler.addFilter(LSPMLoggingFilter())

    # Create LSPM root logger
    logger = getLogger()
    logger.setLevel(LOGGING_LEVEL)
    logger.addHandler(handler)
