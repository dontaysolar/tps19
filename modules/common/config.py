#!/usr/bin/env python3
"""
Centralized configuration and path utilities for TPS systems.
- Resolves TPS_HOME from environment or repository structure
- Exposes standard paths and helpers for databases, logs, and modules
- Provides a helper to add the modules path to sys.path for legacy entrypoints
"""

import os
import sys
from typing import Dict


def _detect_repo_root() -> str:
    # modules/common/config.py -> repo_root is two levels up
    here = os.path.abspath(os.path.dirname(__file__))
    repo_root = os.path.abspath(os.path.join(here, "..", ".."))
    return repo_root


# Base directory for the system; prefer env var, else detect from repo
TPS_HOME: str = os.environ.get("TPS_HOME") or _detect_repo_root()

# Standardized subpaths
PATHS: Dict[str, str] = {
    "home": TPS_HOME,
    "modules": os.path.join(TPS_HOME, "modules"),
    "data": os.path.join(TPS_HOME, "data"),
    "databases": os.path.join(TPS_HOME, "data", "databases"),
    "logs": os.path.join(TPS_HOME, "logs"),
    "config": os.path.join(TPS_HOME, "config"),
    "reports": os.path.join(TPS_HOME, "reports"),
    "patches": os.path.join(TPS_HOME, "patches"),
    "backups": os.path.join(TPS_HOME, "backups"),
}


def ensure_directories() -> None:
    for key in ("data", "databases", "logs", "config", "reports", "patches", "backups"):
        os.makedirs(PATHS[key], exist_ok=True)


def get_db_path(filename: str) -> str:
    """Return absolute path to a database file under the databases directory."""
    ensure_directories()
    return os.path.join(PATHS["databases"], filename)


def add_modules_to_sys_path() -> None:
    """Add modules directory to sys.path if not already present."""
    modules_dir = PATHS["modules"]
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)


# Create standard directories eagerly in most contexts
ensure_directories()
