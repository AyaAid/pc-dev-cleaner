#!/usr/bin/env python3
"""
Dev Cleaner — point d'entrée.
Lance avec : python3 app.py
Puis ouvre http://localhost:5001 dans ton navigateur.
"""
from cleaner import create_app
from cleaner.infrastructure.os_detection import get_platform_info

app = create_app()

if __name__ == "__main__":
    info = get_platform_info()
    print(f"\n🧹 Dev Cleaner démarre sur http://localhost:5001")
    print(f"   OS détecté : {info['os_label']} ({info['node']})\n")
    app.run(debug=True, port=5001)
