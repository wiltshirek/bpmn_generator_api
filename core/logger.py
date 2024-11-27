import logging
import sys
import traceback

# Create logger
logger = logging.getLogger('bpmn_processor')
logger.setLevel(logging.DEBUG)

# Create console handler with formatting
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('=== %(levelname)s === \n%(message)s\n')
console_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(console_handler)

def log_exception(e: Exception):
    """Helper function to log exceptions with full stack trace"""
    logger.error(f"Exception occurred: {str(e)}")
    logger.error("Full stack trace:")
    logger.error("".join(traceback.format_tb(e.__traceback__)))

# Export the logger and helper function
__all__ = ['logger', 'log_exception']

