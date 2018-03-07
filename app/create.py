from importlib import import_module
from logging import StreamHandler, Formatter
from pathlib import Path
from os import remove

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

    # Set logging to standard out
    log_handler = StreamHandler()

    # Set the log format
    formatter = Formatter(app.config['LOG_FORMAT'])
    log_handler.setFormatter(formatter)

    # Set the log level from the config
    app.logger.setLevel(app.config['LOG_LEVEL'])

    # Add the steam log handler to the Flask logger
    app.logger.addHandler(log_handler)

    # Initialize Flask-SQLAlchemy
    db.init_app(app)

    # Create the DB tables if they do not already exist
    db_file = Path(app.config['BASE_DIR'] + '/chat_serv.db')
    if db_file.exists():
        remove(db_file)
        with app.app_context():
            db.create_all()

    return app
