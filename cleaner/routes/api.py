from dataclasses import asdict

import psutil
from flask import Blueprint, jsonify

from cleaner.infrastructure.os_detection import get_platform_info
from cleaner.services.system  import get_system_info
from cleaner.services.scanner import scan_all
from cleaner.services.cleaner import clean_target, clean_all, target_exists

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/platform")
def platform():
    return jsonify(get_platform_info())


@api.route("/system")
def system():
    return jsonify(asdict(get_system_info()))


@api.route("/scan")
def scan():
    results = scan_all()
    return jsonify({k: asdict(v) for k, v in results.items()})


@api.route("/clean/all")
def route_clean_all():
    result = clean_all()
    return jsonify(asdict(result))


@api.route("/clean/<key>")
def route_clean_key(key):
    if not target_exists(key):
        return jsonify({"error": "Cible inconnue"}), 400
    return jsonify(asdict(clean_target(key)))


@api.route("/kill/<int:pid>")
def kill(pid):
    try:
        p = psutil.Process(pid)
        name = p.name()
        p.terminate()
        return jsonify({"ok": True,  "message": f"Arrêt de {name} (PID {pid})"})
    except psutil.NoSuchProcess:
        return jsonify({"ok": False, "message": "Processus introuvable"})
    except psutil.AccessDenied:
        return jsonify({"ok": False, "message": "Accès refusé (processus système)"})
