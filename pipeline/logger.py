import logging
import os
import sys

def get_logger(name: str = "genomic_etl", log_file: str = "outputs/pipeline.log") -> logging.Logger:
    """
    Configures and returns a pipeline-wide logger streaming to console and disk.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger