# 🧹 Mac Dev Cleaner

Application web locale pour nettoyer ton Mac de développeuse.
Interface claymorphisme · Backend Flask · API REST

## Installation

```bash
# 1. Installer les dépendances
pip3 install flask psutil

# 2. Lancer l'app
python3 app.py

# 3. Ouvrir dans le navigateur
open http://localhost:5001
```

## Structure

```
mac_cleaner_app/
├── app.py              ← Backend Flask (API REST)
├── requirements.txt    ← Dépendances Python
├── README.md
└── templates/
    └── index.html      ← Frontend claymorphisme
```

## API endpoints

| Méthode | Route             | Description                        |
|---------|-------------------|------------------------------------|
| GET     | `/`               | Interface web                      |
| GET     | `/api/system`     | RAM, CPU, disque, top processus    |
| GET     | `/api/scan`       | Taille de chaque cible             |
| GET     | `/api/clean/<key>`| Nettoie une cible spécifique       |
| GET     | `/api/clean/all`  | Nettoie toutes les cibles sûres    |
| GET     | `/api/kill/<pid>` | Arrête un processus par PID        |

## Personnalisation

Dans `app.py`, modifie :
- `PROJECTS_ROOT` → chemin de ton dossier de projets (défaut: `~/Projects`)
- `CLEAN_TARGETS` → ajoute/supprime des cibles de nettoyage

## Cibles de nettoyage

| Clé          | Sûr | Description                     |
|--------------|-----|---------------------------------|
| npm          | ✓   | Cache npm/yarn                  |
| gradle       | ✓   | Cache Gradle + logs daemons     |
| pip          | ✓   | Cache pip                       |
| pycache      | ✓   | __pycache__ et .pyc             |
| logs         | ✓   | ~/Library/Logs                  |
| xcode        | ✓   | DerivedData + simulateurs       |
| brew         | ✓   | brew cleanup --prune=all        |
| docker       | ✓   | docker builder prune            |
| trash        | ✓   | Corbeille (~/.Trash)            |
| node_modules | ⚠   | node_modules dans ~/Projects    |
