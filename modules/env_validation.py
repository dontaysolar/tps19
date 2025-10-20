#!/usr/bin/env python3
"""Environment validation utilities for TPS19."""

from __future__ import annotations

import os
from typing import Dict, List

REQUIRED_KEYS = [
    'EXCHANGE_API_KEY',
    'EXCHANGE_API_SECRET',
]

OPTIONAL_KEYS = [
    'TELEGRAM_BOT_TOKEN',
    'TELEGRAM_CHAT_ID',
    'GOOGLE_SHEETS_CREDENTIALS_PATH',
    'GOOGLE_SHEETS_SPREADSHEET_ID',
    'REDIS_URL',
    'REDIS_HOST',
    'REDIS_PORT',
    'REDIS_DB',
    'WEBSOCKET_URL',
    'PORTFOLIO_VALUE',
]

OPTIONAL_PATHS = ['/opt/tps19/config/google_credentials.json']


def validate_required_env() -> Dict[str, List[str]]:
    missing: List[str] = []
    warnings: List[str] = []

    for key in REQUIRED_KEYS:
        if not os.environ.get(key):
            missing.append(key)

    for key in OPTIONAL_KEYS:
        if not os.environ.get(key):
            warnings.append(f"Optional not set: {key}")

    for path in OPTIONAL_PATHS:
        if not os.path.exists(path):
            warnings.append(f"Missing optional file: {path}")

    # If an env-specified credentials path is provided, check it as well
    creds_env = os.environ.get('GOOGLE_SHEETS_CREDENTIALS_PATH')
    if creds_env and not os.path.exists(creds_env):
        warnings.append(f"Missing optional file (from env GOOGLE_SHEETS_CREDENTIALS_PATH): {creds_env}")

    return {'missing': missing, 'warnings': warnings}


def print_validation_summary() -> None:
    result = validate_required_env()
    if result['missing']:
        print("❌ Missing required environment variables:")
        for k in result['missing']:
            print(f"   - {k}")
    else:
        print("✅ Required environment variables present")

    if result['warnings']:
        print("⚠️ Environment warnings:")
        for w in result['warnings']:
            print(f"   - {w}")
    else:
        print("✅ Optional config present")
