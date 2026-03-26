from pathlib import Path
from cleaner.domain.models import CleanTarget
from cleaner.infrastructure.targets.common import (
    gradle_target, pycache_target, node_modules_target, docker_target,
)


def build(home: Path) -> list:
    return [
        CleanTarget(
            key="npm", label="npm / yarn cache",
            paths=[home / ".npm" / "_cacache", home / ".cache" / "yarn"],
            safe=True, color="purple",
        ),
        gradle_target(home),
        CleanTarget(
            key="pip", label="pip cache",
            paths=[home / ".cache" / "pip"],
            safe=True, color="blue",
        ),
        pycache_target(),
        CleanTarget(
            key="logs", label="Cache / Logs",
            paths=[home / ".cache"],
            safe=True, color="purple",
        ),
        CleanTarget(
            key="thumbnails", label="Miniatures (thumbnails)",
            paths=[home / ".cache" / "thumbnails"],
            safe=True, color="green",
        ),
        node_modules_target(),
        CleanTarget(
            key="trash", label="Corbeille (Trash)",
            paths=[
                home / ".local" / "share" / "Trash" / "files",
                home / ".local" / "share" / "Trash" / "info",
            ],
            safe=True, color="red",
        ),
        docker_target(),
    ]
