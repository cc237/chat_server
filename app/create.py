from importlib import import_module

from flask import Flask

from app.blueprints import blueprints
from app.extensions import db
from conf.config import APP_NAME


def create_app():
    """
    Create the Flask application.

    Returns:
        Flask: An instance of the flask application object.
    """

    # Initialize the Flask application
    app = Flask(APP_NAME)

    # Configure the Flask object
    app.config.from_object('conf.config')

    # Import all views and register all Blueprints
    for blueprint in blueprints:
        import_module(blueprint.import_name)
        app.register_blueprint(blueprint)

    # TODO: configure logging

    # Initialize Flask-SQLAlchemy
    db.init_app(app)

    return app
