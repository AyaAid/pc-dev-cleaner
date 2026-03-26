from pathlib import Path
from cleaner.infrastructure.os_detection import HOME

_SEARCH_ROOTS = [HOME / "Projects", HOME / "code", HOME]


def dir_size_bytes(path: Path) -> int:
    total = 0
    try:
        for f in path.rglob("*"):
            if f.is_file() and not f.is_symlink():
                total += f.stat().st_size
    except (PermissionError, OSError):
        pass
    return total


def human(size: int) -> str:
    for unit in ["o", "Ko", "Mo", "Go"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} To"


def find_dynamic(kind: str) -> list:
    root = next((r for r in _SEARCH_ROOTS if r.exists()), HOME)
    found = []
    try:
        if kind == "node_modules":
            for p in root.rglob("node_modules"):
                if p.is_dir() and ".git" not in str(p):
                    found.append(p)
        elif kind == "__pycache__":
            found += [p for p in root.rglob("__pycache__")]
            found += [p for p in root.rglob("*.pyc")]
    except (PermissionError, OSError):
        pass
    return found
