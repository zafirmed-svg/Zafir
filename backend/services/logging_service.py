import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def log_error(location: str, error: Exception):
    logger.error(f"Error in {location}: {str(error)}", exc_info=True)
