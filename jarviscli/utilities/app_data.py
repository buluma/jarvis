"""Resolve Jarvis' per-user data directory without relying on the cwd."""

import os
import sys
from pathlib import Path


def user_data_dir():
    override = os.environ.get("JARVIS_DATA_DIR")
    if override:
        return Path(override).expanduser()

    if sys.platform == "win32":
        root = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        return (Path(root) if root else Path.home() / "AppData" / "Local") / "Jarvis"

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Jarvis"

    root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return root / "jarvis"
