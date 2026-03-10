import logging
import os

def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a logger that:
    - prints messages to the terminal (console)
    - saves messages to a file called automation.log
    """

    # Create a logger with the given name (usually the module name)
    logger = logging.getLogger(name)

    # Only add handlers if they haven't been added already
    # (prevents duplicate log lines if this function is called multiple times)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # --- Format: timestamp | level | message ---
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # --- Handler 1: print to terminal ---
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)

        # --- Handler 2: save to log file ---
        log_file = os.path.join(os.path.dirname(__file__), "..", "automation.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
