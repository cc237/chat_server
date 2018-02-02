from pathlib import Path

from app.create import create_app
from app.extensions import db

application = create_app()

if __name__ == '__main__':

    # Initialize the DB if it does not already exist
    db_file = Path(application.config['BASE_DIR'] + '/chat_serv.db')
    if not db_file.exists():
        db.create_all(app=create_app())

    # Run the application
    application.run()
