import logging

from app.config import settings

logger = logging.getLogger(__name__)

logger.setLevel(settings.log_level)

info = logger.info
debug = logger.debug
warning = logger.warning
error = logger.error
__all__ = ["info", "debug", "warning", "error"]
