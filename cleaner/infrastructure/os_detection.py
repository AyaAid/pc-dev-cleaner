import os
import platform
from pathlib import Path

SYSTEM: str = platform.system()   # 'Darwin' | 'Linux' | 'Windows'
HOME:   Path = Path.home()

_OS_LABELS = {"Darwin": "macOS", "Linux": "Linux", "Windows": "Windows"}


def get_disk_root() -> str:
    if SYSTEM == "Windows":
        return os.environ.get("SystemDrive", "C:") + "\\"
    return "/"


def get_platform_info() -> dict:
    return {
        "os":       SYSTEM,
        "os_label": _OS_LABELS.get(SYSTEM, SYSTEM),
        "os_full":  platform.platform(),
        "node":     platform.node(),
        "python":   platform.python_version(),
    }
