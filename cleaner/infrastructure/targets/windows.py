import os
from pathlib import Path
from cleaner.domain.models import CleanTarget
from cleaner.infrastructure.targets.common import (
    gradle_target, pycache_target, node_modules_target, docker_target,
)


def build(home: Path) -> list:
    temp = Path(os.environ.get("TEMP", str(home / "AppData" / "Local" / "Temp")))
    return [
        CleanTarget(
            key="npm", label="npm / yarn cache",
            paths=[
                home / "AppData" / "Roaming" / "npm-cache",
                home / "AppData" / "Local"   / "Yarn" / "Cache",
            ],
            safe=True, color="purple",
        ),
        gradle_target(home),
        CleanTarget(
            key="pip", label="pip cache",
            paths=[home / "AppData" / "Local" / "pip" / "Cache"],
            safe=True, color="blue",
        ),
        pycache_target(),
        CleanTarget(
            key="wintemp", label="Fichiers temporaires (Temp)",
            paths=[temp],
            safe=True, color="amber",
        ),
        node_modules_target(),
        CleanTarget(
            key="trash", label="Corbeille (Recycle Bin)",
            paths=[], safe=True, color="red",
            command=(
                'PowerShell.exe -NoProfile -Command '
                '"Clear-RecycleBin -Force -ErrorAction SilentlyContinue"'
            ),
        ),
        docker_target(),
    ]
