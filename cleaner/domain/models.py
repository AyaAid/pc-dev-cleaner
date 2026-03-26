from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class CleanTarget:
    key:     str
    label:   str
    paths:   list
    safe:    bool
    color:   str
    dynamic: Optional[str] = None
    command: Optional[str] = None


@dataclass
class ScanResult:
    key:         str
    label:       str
    size_bytes:  int
    size_human:  str
    safe:        bool
    color:       str
    paths_count: int


@dataclass
class CleanResult:
    key:          str
    freed_bytes:  int
    freed_human:  str
    log:          list


@dataclass
class ProcessInfo:
    pid:    int
    name:   str
    mem_mb: int
    cpu:    float


@dataclass
class DiskStats:
    total_gb: float
    used_gb:  float
    free_gb:  float
    percent:  float


@dataclass
class RamStats:
    total_gb: float
    used_gb:  float
    free_gb:  float
    percent:  float


@dataclass
class SystemStats:
    disk:      DiskStats
    ram:       RamStats
    cpu:       float
    processes: list
