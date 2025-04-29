from rich.logging import RichHandler
import logging, sys

def setup_logger(name="dscim", level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        handler = RichHandler(
            show_time=True, show_level=True, show_path=False, rich_tracebacks=True, stream=sys.stdout
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    return logger
