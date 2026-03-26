"""
Cibles cross-platform : même configuration sur tous les OS.
Importées par chaque fichier OS pour composer la liste finale.
"""
from pathlib import Path
from cleaner.domain.models import CleanTarget


def gradle_target(home: Path) -> CleanTarget:
    return CleanTarget(
        key="gradle", label="Gradle cache",
        paths=[home / ".gradle" / "caches", home / ".gradle" / "daemon"],
        safe=True, color="green",
    )


def pycache_target() -> CleanTarget:
    return CleanTarget(
        key="pycache", label="__pycache__ & .pyc",
        paths=[], safe=True, color="amber", dynamic="__pycache__",
    )


def node_modules_target() -> CleanTarget:
    return CleanTarget(
        key="node_modules", label="node_modules (projets)",
        paths=[], safe=False, color="red", dynamic="node_modules",
    )


def docker_target() -> CleanTarget:
    return CleanTarget(
        key="docker", label="Docker builder cache",
        paths=[], safe=True, color="blue",
        command="docker builder prune -f",
    )
