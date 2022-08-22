# configuration.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Access and update items in a configuration file.

The initial values are taken from file named in self._CONFIGURATION in the
user's home directory if the file exists.

"""
# This gets a pylint no-name-in-module report but the code runs.
from solentware_misc.core import configuration

from . import constants


class Configuration(
    configuration.Configuration
):  # pylint: disable=too-few-public-methods
    """Identify configuration file and access and update item values."""

    _CONFIGURATION = ".ecfformat.conf"
    _DEFAULT_ITEM_VAULES = (
        (constants.RECENT_RESULTS_FORMAT_FILE, "~"),
        (constants.SHOW_VALUE_BOUNDARY, constants.SHOW_VALUE_BOUNDARY_TRUE),
        (constants.CHECK_NAME_COUNT, constants.CHECK_NAME_COUNT_FALSE),
    )
