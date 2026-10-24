from flask import Flask

from .db import initialize_database


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=app.instance_path + "/local_shop.sqlite3",
        SECRET_KEY=None,
    )
    if test_config:
        app.config.update(test_config)

    # Flask's instance folder is the persistent, machine-local data boundary.
    app.config["DATABASE"] = str(app.config["DATABASE"])
    initialize_database(app)

    from .routes import bp

    app.register_blueprint(bp)
    return app
