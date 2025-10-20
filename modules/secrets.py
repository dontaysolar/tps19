#!/usr/bin/env python3
"""Secrets helper with optional Secret Manager support.

Order of resolution:
1) Environment variable
2) Google Secret Manager (if SECRET_MANAGER=GCP and library configured)
3) Fallback: None
"""
from __future__ import annotations

import os
from typing import Optional


def get_secret(name: str) -> Optional[str]:
    # First, env var
    v = os.environ.get(name)
    if v:
        return v

    # Optional: Google Secret Manager
    if os.environ.get('SECRET_MANAGER', '').upper() == 'GCP':
        try:
            from google.cloud import secretmanager  # type: ignore
            client = secretmanager.SecretManagerServiceClient()
            project_id = os.environ.get('GCP_PROJECT')
            if not project_id:
                return None
            # Secret resource name must exist: projects/{project}/secrets/{name}/versions/latest
            sec_name = f"projects/{project_id}/secrets/{name}/versions/latest"
            resp = client.access_secret_version(name=sec_name)
            return resp.payload.data.decode('utf-8')
        except Exception:
            return None

    return None
