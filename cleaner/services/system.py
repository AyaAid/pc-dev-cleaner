import psutil
from cleaner.domain.models import SystemStats, DiskStats, RamStats, ProcessInfo
from cleaner.infrastructure.os_detection import get_disk_root


def get_system_info() -> SystemStats:
    disk = psutil.disk_usage(get_disk_root())
    mem  = psutil.virtual_memory()
    cpu  = psutil.cpu_percent(interval=0.5)

    processes = _top_processes()

    return SystemStats(
        disk=DiskStats(
            total_gb=round(disk.total / 1e9, 1),
            used_gb =round(disk.used  / 1e9, 1),
            free_gb =round(disk.free  / 1e9, 1),
            percent =disk.percent,
        ),
        ram=RamStats(
            total_gb=round(mem.total     / 1e9, 1),
            used_gb =round(mem.used      / 1e9, 1),
            free_gb =round(mem.available / 1e9, 1),
            percent =mem.percent,
        ),
        cpu=cpu,
        processes=processes,
    )


def _top_processes(n: int = 12) -> list:
    procs = []
    for p in sorted(
        psutil.process_iter(["pid", "name", "memory_info", "cpu_percent"]),
        key=lambda x: x.info["memory_info"].rss if x.info["memory_info"] else 0,
        reverse=True,
    )[:n]:
        try:
            procs.append(ProcessInfo(
                pid    =p.info["pid"],
                name   =p.info["name"][:28],
                mem_mb =round(p.info["memory_info"].rss / 1024 / 1024),
                cpu    =round(p.cpu_percent(), 1),
            ))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return procs
