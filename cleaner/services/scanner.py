from cleaner.domain.models import CleanTarget, ScanResult
from cleaner.infrastructure.filesystem import dir_size_bytes, find_dynamic, human
from cleaner.infrastructure.targets import TARGETS


def scan_all() -> dict:
    return {key: _scan_one(key, target) for key, target in TARGETS.items()}


def _scan_one(key: str, target: CleanTarget) -> ScanResult:
    # Cibles nettoyées via commande shell : taille non calculable à l'avance
    if target.command and not target.paths:
        return ScanResult(
            key=key, label=target.label,
            size_bytes=0, size_human="via commande",
            safe=target.safe, color=target.color, paths_count=1,
        )

    paths = find_dynamic(target.dynamic) if target.dynamic else list(target.paths)
    total = sum(dir_size_bytes(p) for p in paths if p.exists())

    return ScanResult(
        key=key, label=target.label,
        size_bytes=total, size_human=human(total),
        safe=target.safe, color=target.color,
        paths_count=len([p for p in paths if p.exists()]),
    )
