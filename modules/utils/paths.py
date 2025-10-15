#!/usr/bin/env python3
"""Shared path utilities for TPS systems.

Resolves a writable base directory for both production (/opt/tps19)
and development (repo workspace) without requiring code changes.
"""

import os
from typing import Optional


def get_base_dir() -> str:
    """Return the TPS base directory.

    Priority:
    1) TPS19_BASE_DIR env var
    2) /opt/tps19 if it exists
    3) repo root inferred from this file
    """
    env_dir = os.environ.get("TPS19_BASE_DIR")
    if env_dir:
        return env_dir

    opt_dir = "/opt/tps19"
    if os.path.isdir(opt_dir):
        return opt_dir

    # Fallback to repo root (modules/utils -> repo)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def data_dir(subdir: Optional[str] = None) -> str:
    base = os.path.join(get_base_dir(), "data")
    if subdir:
        return _ensure_dir(os.path.join(base, subdir))
    return _ensure_dir(base)


def db_dir() -> str:
    return data_dir("databases")


def db_path(filename: str) -> str:
    return os.path.join(db_dir(), filename)


def config_dir() -> str:
    return _ensure_dir(os.path.join(get_base_dir(), "config"))


def config_path(filename: str) -> str:
    return os.path.join(config_dir(), filename)


def logs_dir() -> str:
    return _ensure_dir(os.path.join(get_base_dir(), "logs"))


def logs_path(filename: str) -> str:
    return os.path.join(logs_dir(), filename)


def backups_dir() -> str:
    return _ensure_dir(os.path.join(get_base_dir(), "backups"))


def patches_dir() -> str:
    return _ensure_dir(os.path.join(get_base_dir(), "patches"))


def system_dir() -> str:
    return get_base_dir()
