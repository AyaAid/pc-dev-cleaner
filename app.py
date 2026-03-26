#!/usr/bin/env python3
"""
Dev Cleaner — Flask backend (cross-platform : macOS, Linux, Windows)
Lance avec : python3 app.py
Puis ouvre http://localhost:5001 dans ton navigateur.
"""

import os
import platform
import shutil
import subprocess
import json
import psutil
from pathlib import Path
from flask import Flask, jsonify, render_template
import queue, threading

app = Flask(__name__)
HOME   = Path.home()
SYSTEM = platform.system()   # 'Darwin' | 'Linux' | 'Windows'
PROJECTS_ROOT = HOME / "Projects"

# ── Chemins selon l'OS ─────────────────────────────────────────────────────────
def _disk_root() -> str:
    if SYSTEM == "Windows":
        return os.environ.get("SystemDrive", "C:") + "\\"
    return "/"

def _npm_paths() -> list:
    if SYSTEM == "Darwin":
        return [HOME / ".npm" / "_cacache", HOME / "Library" / "Caches" / "yarn"]
    if SYSTEM == "Linux":
        return [HOME / ".npm" / "_cacache", HOME / ".cache" / "yarn"]
    return [HOME / "AppData" / "Roaming" / "npm-cache",
            HOME / "AppData" / "Local"   / "Yarn" / "Cache"]

def _pip_paths() -> list:
    if SYSTEM == "Darwin":
        return [HOME / "Library" / "Caches" / "pip"]
    if SYSTEM == "Linux":
        return [HOME / ".cache" / "pip"]
    return [HOME / "AppData" / "Local" / "pip" / "Cache"]

def _logs_paths() -> list:
    if SYSTEM == "Darwin":
        return [HOME / "Library" / "Logs"]
    if SYSTEM == "Linux":
        return [HOME / ".cache"]
    return [Path(os.environ.get("TEMP", str(HOME / "AppData" / "Local" / "Temp")))]

def _trash_entry() -> dict:
    base = {"label": "Corbeille", "safe": True, "color": "red"}
    if SYSTEM == "Darwin":
        return {**base, "paths": [],
                "command": "rm -rf ~/.Trash/* ~/.Trash/.*  2>/dev/null; true"}
    if SYSTEM == "Linux":
        return {**base, "label": "Corbeille (Trash)",
                "paths": [HOME / ".local" / "share" / "Trash" / "files",
                           HOME / ".local" / "share" / "Trash" / "info"]}
    # Windows
    return {**base, "label": "Corbeille (Recycle Bin)", "paths": [],
            "command": 'PowerShell.exe -NoProfile -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"'}

# ── Construction des cibles ────────────────────────────────────────────────────
def _build_targets() -> dict:
    t = {}

    t["npm"] = {
        "label": "npm / yarn cache",
        "paths": _npm_paths(),
        "safe": True, "color": "purple",
    }
    t["gradle"] = {
        "label": "Gradle cache",
        "paths": [HOME / ".gradle" / "caches", HOME / ".gradle" / "daemon"],
        "safe": True, "color": "green",
    }
    t["pip"] = {
        "label": "pip cache",
        "paths": _pip_paths(),
        "safe": True, "color": "blue",
    }
    t["pycache"] = {
        "label": "__pycache__ & .pyc",
        "paths": [], "safe": True, "color": "amber",
        "dynamic": "__pycache__",
    }
    t["logs"] = {
        "label": "Logs système" if SYSTEM == "Darwin" else "Cache / Logs",
        "paths": _logs_paths(),
        "safe": True, "color": "purple",
    }

    # ── macOS uniquement ──
    if SYSTEM == "Darwin":
        t["xcode"] = {
            "label": "Xcode DerivedData",
            "paths": [HOME / "Library" / "Developer" / "Xcode" / "DerivedData",
                      HOME / "Library" / "Developer" / "CoreSimulator" / "Caches"],
            "safe": True, "color": "green",
        }
        t["brew"] = {
            "label": "Homebrew cache",
            "paths": [], "safe": True, "color": "amber",
            "command": "brew cleanup --prune=all -q",
        }

    # ── Linux uniquement ──
    if SYSTEM == "Linux":
        t["thumbnails"] = {
            "label": "Miniatures (thumbnails)",
            "paths": [HOME / ".cache" / "thumbnails"],
            "safe": True, "color": "green",
        }

    # ── Windows uniquement ──
    if SYSTEM == "Windows":
        t["wintemp"] = {
            "label": "Fichiers temporaires (Temp)",
            "paths": [Path(os.environ.get("TEMP",
                           str(HOME / "AppData" / "Local" / "Temp")))],
            "safe": True, "color": "amber",
        }

    t["node_modules"] = {
        "label": "node_modules (projets)",
        "paths": [], "safe": False, "color": "red",
        "dynamic": "node_modules",
    }
    t["trash"]  = _trash_entry()
    t["docker"] = {
        "label": "Docker builder cache",
        "paths": [], "safe": True, "color": "blue",
        "command": "docker builder prune -f",
    }
    return t

CLEAN_TARGETS = _build_targets()
DISK_ROOT     = _disk_root()

# ── Utilitaires ────────────────────────────────────────────────────────────────
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
    root = PROJECTS_ROOT if PROJECTS_ROOT.exists() else HOME / "code"
    if not root.exists():
        root = HOME
    found = []
    try:
        if kind == "node_modules":
            for p in root.rglob("node_modules"):
                if p.is_dir() and ".git" not in str(p):
                    found.append(p)
        elif kind == "__pycache__":
            for p in root.rglob("__pycache__"):
                found.append(p)
            for p in root.rglob("*.pyc"):
                found.append(p)
    except (PermissionError, OSError):
        pass
    return found

# ── Routes API ─────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/platform")
def platform_info():
    """Retourne l'OS détecté, le nom de la machine et la version Python."""
    os_labels = {"Darwin": "macOS", "Linux": "Linux", "Windows": "Windows"}
    return jsonify({
        "os":       SYSTEM,
        "os_label": os_labels.get(SYSTEM, SYSTEM),
        "os_full":  platform.platform(),
        "node":     platform.node(),
        "python":   platform.python_version(),
    })

@app.route("/api/system")
def system_info():
    disk = psutil.disk_usage(DISK_ROOT)
    mem  = psutil.virtual_memory()
    cpu  = psutil.cpu_percent(interval=0.5)

    procs = []
    for p in sorted(
        psutil.process_iter(["pid", "name", "memory_info", "cpu_percent", "status"]),
        key=lambda x: x.info["memory_info"].rss if x.info["memory_info"] else 0,
        reverse=True
    )[:12]:
        try:
            procs.append({
                "pid":    p.info["pid"],
                "name":   p.info["name"][:28],
                "mem_mb": round(p.info["memory_info"].rss / 1024 / 1024),
                "cpu":    round(p.cpu_percent(), 1),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return jsonify({
        "disk": {
            "total_gb": round(disk.total / 1e9, 1),
            "used_gb":  round(disk.used  / 1e9, 1),
            "free_gb":  round(disk.free  / 1e9, 1),
            "percent":  disk.percent,
        },
        "ram": {
            "total_gb": round(mem.total     / 1e9, 1),
            "used_gb":  round(mem.used      / 1e9, 1),
            "free_gb":  round(mem.available / 1e9, 1),
            "percent":  mem.percent,
        },
        "cpu":       cpu,
        "processes": procs,
    })

@app.route("/api/scan")
def scan():
    results = {}
    for key, cfg in CLEAN_TARGETS.items():
        paths = list(cfg["paths"])
        if "dynamic" in cfg:
            paths = find_dynamic(cfg["dynamic"])

        if "command" in cfg:
            results[key] = {
                "label":       cfg["label"],
                "size_bytes":  0,
                "size_human":  "via commande",
                "safe":        cfg["safe"],
                "color":       cfg["color"],
                "paths_count": 1,
            }
            continue

        total = sum(dir_size_bytes(p) for p in paths if p.exists())
        results[key] = {
            "label":       cfg["label"],
            "size_bytes":  total,
            "size_human":  human(total),
            "safe":        cfg["safe"],
            "color":       cfg["color"],
            "paths_count": len([p for p in paths if p.exists()]),
        }
    return jsonify(results)

@app.route("/api/clean/<key>")
def clean_key(key):
    if key not in CLEAN_TARGETS:
        return jsonify({"error": "Cible inconnue"}), 400

    cfg  = CLEAN_TARGETS[key]
    freed = 0
    log  = []

    if "command" in cfg:
        try:
            subprocess.run(cfg["command"], shell=True, check=True,
                           capture_output=True, timeout=60)
            log.append(f"OK : {cfg['command']}")
        except Exception as e:
            log.append(f"Erreur : {e}")
    else:
        paths = list(cfg["paths"])
        if "dynamic" in cfg:
            paths = find_dynamic(cfg["dynamic"])

        for p in paths:
            if not p.exists():
                continue
            size = dir_size_bytes(p)
            try:
                if p.is_dir():
                    for child in p.iterdir():
                        child_size = dir_size_bytes(child)
                        try:
                            if child.is_dir():
                                shutil.rmtree(child)
                            else:
                                child.unlink()
                            freed += child_size
                        except Exception:
                            pass
                    log.append(f"Nettoyé : {p.name} ({human(size)})")
                else:
                    p.unlink()
                    freed += size
                    log.append(f"Supprimé : {p.name} ({human(size)})")
            except Exception as e:
                log.append(f"Erreur sur {p.name} : {e}")

    return jsonify({"key": key, "freed_bytes": freed,
                    "freed_human": human(freed), "log": log})

@app.route("/api/clean/all")
def clean_all():
    total = 0
    log   = []
    for key in CLEAN_TARGETS:
        r    = app.test_client().get(f"/api/clean/{key}")
        data = r.get_json()
        total += data.get("freed_bytes", 0)
        log.extend(data.get("log", []))
    return jsonify({"freed_bytes": total, "freed_human": human(total), "log": log})

@app.route("/api/kill/<int:pid>")
def kill_process(pid):
    try:
        p    = psutil.Process(pid)
        name = p.name()
        p.terminate()
        return jsonify({"ok": True,  "message": f"Arrêt de {name} (PID {pid})"})
    except psutil.NoSuchProcess:
        return jsonify({"ok": False, "message": "Processus introuvable"})
    except psutil.AccessDenied:
        return jsonify({"ok": False, "message": "Accès refusé (processus système)"})

if __name__ == "__main__":
    os_labels = {"Darwin": "macOS", "Linux": "Linux", "Windows": "Windows"}
    print(f"\n🧹 Dev Cleaner démarre sur http://localhost:5001")
    print(f"   OS détecté : {os_labels.get(SYSTEM, SYSTEM)} ({platform.node()})\n")
    app.run(debug=True, port=5001)
