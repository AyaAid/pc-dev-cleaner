from cleaner.domain.models import CleanTarget
from cleaner.infrastructure.os_detection import SYSTEM, HOME
from cleaner.infrastructure.targets import macos, linux, windows

_BUILDERS = {
    "Darwin":  macos.build,
    "Linux":   linux.build,
    "Windows": windows.build,
}


def _build() -> dict:
    builder = _BUILDERS.get(SYSTEM, linux.build)  # fallback Linux
    return {t.key: t for t in builder(HOME)}


# Registre unique, construit une seule fois au démarrage
TARGETS: dict = _build()
