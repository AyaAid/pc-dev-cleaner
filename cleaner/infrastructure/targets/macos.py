from pathlib import Path
from cleaner.domain.models import CleanTarget
from cleaner.infrastructure.targets.common import (
    gradle_target, pycache_target, node_modules_target, docker_target,
)


def build(home: Path) -> list:
    return [
        CleanTarget(
            key="npm", label="npm / yarn cache",
            paths=[home / ".npm" / "_cacache", home / "Library" / "Caches" / "yarn"],
            safe=True, color="purple",
        ),
        gradle_target(home),
        CleanTarget(
            key="pip", label="pip cache",
            paths=[home / "Library" / "Caches" / "pip"],
            safe=True, color="blue",
        ),
        pycache_target(),
        CleanTarget(
            key="logs", label="Logs système",
            paths=[home / "Library" / "Logs"],
            safe=True, color="purple",
        ),
        CleanTarget(
            key="xcode", label="Xcode DerivedData",
            paths=[
                home / "Library" / "Developer" / "Xcode" / "DerivedData",
                home / "Library" / "Developer" / "CoreSimulator" / "Caches",
            ],
            safe=True, color="green",
        ),
        CleanTarget(
            key="brew", label="Homebrew cache",
            paths=[], safe=True, color="amber",
            command="brew cleanup --prune=all -q",
        ),
        node_modules_target(),
        CleanTarget(
            key="trash", label="Corbeille",
            paths=[], safe=True, color="red",
            command="rm -rf ~/.Trash/* ~/.Trash/.*  2>/dev/null; true",
        ),
        docker_target(),
    ]
