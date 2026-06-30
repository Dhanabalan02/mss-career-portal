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
