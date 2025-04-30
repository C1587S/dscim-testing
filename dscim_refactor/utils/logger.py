# File: utils/logger.py

import logging
import warnings
from rich.logging import RichHandler

# Capture warnings into logging
logging.captureWarnings(True)

def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    Sets up a clean, Rich-colored logger with warnings capture.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = RichHandler(
            rich_tracebacks=True,
            markup=True,
            show_time=True,
            show_level=True,
            show_path=False,
            log_time_format="[%X]",
            omit_repeated_times=False,
            # Customize rich handler if needed
        )
        formatter = logging.Formatter(
            "%(message)s", datefmt="[%X]"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Redirect captured warnings (py.warnings) to use the same handler
        warnings_logger = logging.getLogger("py.warnings")
        warnings_logger.handlers.clear()
        warnings_logger.addHandler(handler)
        warnings_logger.setLevel(level)

    return logger

# Optionally filter known noisy warnings
warnings.filterwarnings("ignore", message=".*vlen-utf8.*")
warnings.filterwarnings("ignore", message=".*Consolidated metadata is currently not part of the Zarr format 3 specification.*")
