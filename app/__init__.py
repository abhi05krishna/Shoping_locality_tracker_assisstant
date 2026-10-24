import secrets

from flask import Flask

from .db import initialize_database


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=app.instance_path + "/local_shop.sqlite3",
        # A new signing key per process intentionally expires vendor unlocks on restart.
        SECRET_KEY=secrets.token_urlsafe(32),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if test_config:
        app.config.update(test_config)

    # Flask's instance folder is the persistent, machine-local data boundary.
    app.config["DATABASE"] = str(app.config["DATABASE"])
    initialize_database(app)

    from .routes import bp

    app.register_blueprint(bp)
    return app
