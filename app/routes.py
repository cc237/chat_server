from flask import jsonify

from app.blueprints import bp


@bp.route('/health_check', methods=['GET', 'POST'])
def health_check():
    """Returns a simple JSON response if the app is online."""

    return jsonify(dict(status='success')), 200
