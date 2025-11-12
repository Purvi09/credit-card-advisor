import logging
import os

def get_logger(name=__name__):
    log_path = os.path.join(os.path.dirname(__file__), "app.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(name)

logger = get_logger()