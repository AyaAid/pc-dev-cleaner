from pathlib import Path
from flask import Flask, render_template

_ROOT = Path(__file__).parent.parent


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(_ROOT / "templates"),
        static_folder=str(_ROOT / "static"),
    )

    from cleaner.routes.api import api
    app.register_blueprint(api)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
