"""A Python-based API for Using Renderbus cloud rendering houdini service."""

# pylint: disable=import-error
from pkg_resources import DistributionNotFound, get_distribution

from rayvision_log import init_logger

from rayvision_clarisse.constants import PACKAGE_NAME

# Initialize the logger.
init_logger(PACKAGE_NAME)

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # Package is not installed.
    __version__ = '0.0.0-dev.1'
