#!/usr/bin/env python3
"""
Shared logging setup.
- Unified formatting
- Per-module logger getter
- Optional file handler to logs directory
"""

import logging
import os
from .config import PATHS, ensure_directories


def get_logger(name: str, to_file: bool = True, level: int = logging.INFO) -> logging.Logger:
    ensure_directories()

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if to_file:
        try:
            log_file = os.path.join(PATHS["logs"], f"{name.replace('.', '_')}.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            # Fail open: still log to console
            pass

    return logger
