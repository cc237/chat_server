"""All Flask blueprints are defined here."""

from flask import Blueprint

#: List of all blueprints for the application
blueprints = []

#: The only blueprint used in this application
bp = Blueprint(name='bp', import_name='app.routes')

# Append all blueprints to the list
blueprints.append(bp)
