import os


def _can_create(path: str) -> bool:
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False


def get_base_dir() -> str:
    # Prefer env override
    env_base = os.getenv("TPS19_BASE_DIR")
    if env_base and _can_create(env_base):
        return env_base

    # Try default
    default = "/opt/tps19"
    if _can_create(default):
        return default

    # Fallback to workspace-local directory
    fallback = os.path.join(os.getcwd(), ".tps19")
    os.makedirs(fallback, exist_ok=True)
    return fallback


def path(relative_path: str, ensure_dir: bool = False) -> str:
    rel = relative_path.lstrip("/")
    absolute = os.path.join(get_base_dir(), rel)
    if ensure_dir:
        os.makedirs(os.path.dirname(absolute), exist_ok=True)
    return absolute
