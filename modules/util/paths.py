#!/usr/bin/env python3
"""Path utilities for TPS19.

Determines a writable base directory for runtime data and reports.
Order of precedence:
1) Environment variable TPS19_BASE_DIR if set
2) Writable '/opt/tps19' if available
3) Project-local fallback '<repo>/.tps19'
"""
import os
from typing import Tuple


def _is_writable(path: str) -> bool:
    try:
        os.makedirs(path, exist_ok=True)
        test_file = os.path.join(path, '.write_test')
        with open(test_file, 'w') as f:
            f.write('ok')
        os.remove(test_file)
        return True
    except Exception:
        return False


def get_base_dir() -> str:
    env_dir = os.getenv('TPS19_BASE_DIR')
    if env_dir:
        try:
            os.makedirs(env_dir, exist_ok=True)
        except Exception:
            pass
        return env_dir
    opt_dir = '/opt/tps19'
    if _is_writable(opt_dir):
        return opt_dir
    repo_dir = os.getenv('TPS19_REPO_DIR') or os.getcwd()
    fallback = os.path.join(repo_dir, '.tps19')
    os.makedirs(fallback, exist_ok=True)
    return fallback


def data_path(*parts: str) -> str:
    return os.path.join(get_base_dir(), 'data', *parts)


def config_path(*parts: str) -> str:
    return os.path.join(get_base_dir(), 'config', *parts)


def logs_path(*parts: str) -> str:
    return os.path.join(get_base_dir(), 'logs', *parts)


def reports_path(*parts: str) -> str:
    return os.path.join(get_base_dir(), 'reports', *parts)
