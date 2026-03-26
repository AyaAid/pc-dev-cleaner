import shutil
import subprocess
from pathlib import Path

from cleaner.domain.models import CleanTarget, CleanResult
from cleaner.infrastructure.filesystem import dir_size_bytes, find_dynamic, human
from cleaner.infrastructure.targets import TARGETS


def target_exists(key: str) -> bool:
    return key in TARGETS


def clean_target(key: str) -> CleanResult:
    target = TARGETS[key]

    if target.command:
        freed, log = _run_command(target.command)
    else:
        paths = find_dynamic(target.dynamic) if target.dynamic else list(target.paths)
        freed, log = _clean_paths(paths)

    return CleanResult(key=key, freed_bytes=freed, freed_human=human(freed), log=log)


def clean_all() -> CleanResult:
    total_freed, all_logs = 0, []
    for key in TARGETS:
        result = clean_target(key)
        total_freed += result.freed_bytes
        all_logs.extend(result.log)
    return CleanResult(key="all", freed_bytes=total_freed,
                       freed_human=human(total_freed), log=all_logs)


# ── Helpers privés ─────────────────────────────────────────────────────────────

def _run_command(command: str) -> tuple:
    try:
        subprocess.run(command, shell=True, check=True,
                       capture_output=True, timeout=60)
        return 0, [f"OK : {command}"]
    except Exception as e:
        return 0, [f"Erreur : {e}"]


def _clean_paths(paths: list) -> tuple:
    freed, log = 0, []
    for p in paths:
        if not p.exists():
            continue
        size = dir_size_bytes(p)
        try:
            if p.is_dir():
                freed += _clean_directory(p)
                log.append(f"Nettoyé : {p.name} ({human(size)})")
            else:
                p.unlink()
                freed += size
                log.append(f"Supprimé : {p.name} ({human(size)})")
        except Exception as e:
            log.append(f"Erreur sur {p.name} : {e}")
    return freed, log


def _clean_directory(directory: Path) -> int:
    freed = 0
    for child in directory.iterdir():
        child_size = dir_size_bytes(child)
        try:
            shutil.rmtree(child) if child.is_dir() else child.unlink()
            freed += child_size
        except Exception:
            pass
    return freed
