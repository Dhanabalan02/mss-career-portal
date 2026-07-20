import logging
import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent

LOG_FILE_PATH = APP_DIR / "app.log"

def setup_logger():
    """Configures application-wide logging to console and a file in the app folder."""
    root = logging.getLogger()

    if root.handlers:
        return logging.getLogger("fastapi_app")

    root.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    return logging.getLogger("fastapi_app")

logger = setup_logger()

def setup_offer_logger():
    """Configures logging for offer service to a separate file."""
    offer_logger = logging.getLogger("offer_service")
    if offer_logger.handlers:
        return offer_logger

    offer_logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    log_file_path = APP_DIR / "offer_service.log"
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    offer_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    offer_logger.addHandler(console_handler)

    offer_logger.propagate = False

    return offer_logger

offer_logger = setup_offer_logger()
