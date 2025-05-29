import sys
from pathlib import Path

# Add the /src folder to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from myproject.cli_logger_utils import setup_logging
import logging

setup_logging()
logger = logging.getLogger("myproject")

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
