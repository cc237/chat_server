from bcrypt import gensalt, hashpw
from flask import current_app as app, jsonify, request
from sqlalchemy import and_
from sqlalchemy.sql import exists

from app.blueprints import bp
from app.extensions import db
from app.models import PendingMessage, User


# TODO: Need to have "friends list" with add and remove
# TODO: Need to have voice and image messaging
# TODO: Write generic function to validate the request parameters
# TODO: Remove the "show_pending" route

@bp.route('/show_pending', methods=['GET'])
def show_pending():
    """Returns all pending messages."""

    app.logger.debug('API call to /show_pending')

    all_msgs = PendingMessage.query.all()
    return jsonify(
        dict(status='success', msgs=[msg.message for msg in all_msgs])
    ), 200


@bp.route('/users', methods=['GET'])
def users():
    """Returns all registered users."""

    all_users = User.query.all()
    return jsonify(
        dict(status='success', users=[user.username for user in all_users])
    ), 200


@bp.route('/login', methods=['POST'])
def login():
    """Validate a user's credentials for authorization"""

    # Return a failure for an invalid request
    try:
        un = request.form['un']
        pw = request.form['pw']
    except Exception as e:
        return jsonify(
            dict(status='failure', auth=False, reason=str(e))
        ), 400

    # Query for the user
    user = db.session.query(User).filter(User.username == un).first()

    # Try to log the user in if they exist. Return a failure if the
    if user:
        if hashpw(pw.encode('utf-8'), user.pw_hash) == user.pw_hash:
            return jsonify(
                dict(status='success', auth=True, reason='valid credentials')
            ), 200
        else:
            return jsonify(
                dict(status='failure', auth=False, reason='auth failure')
            ),
    else:
        return jsonify(
            dict(status='failure', auth=False, reason='auth failure')
        ), 401


@bp.route('/register', methods=['POST'])
def register():
    """Registers a new user of the chat application."""

    # Return a failure for an invalid request
    try:
        un = request.form['un']
        pw = request.form['pw']
    except Exception as e:
        return jsonify(
            dict(status='failure', registered=False, reason=str(e))
        ), 400

    # Check if the user already exists and register them if they do not already
    # exist. Otherwise, return a failure indicating that the user exists.
    user_found = db.session.query(exists().where(User.username == un)).scalar()
    if not user_found:
        db.session.add(
            User(
                username=un, pw_hash=hashpw(pw.encode('utf-8'), gensalt())
            )
        )
        db.session.commit()
        return jsonify(
            dict(status='success', registered=True, reason='valid new user')
        ), 200
    else:
        return jsonify(
            dict(status='failure', registered=False, reason='user exists')
        ), 403


@bp.route('/send_msg', methods=['POST'])
def send_msg():
    """Send a text message to a given user."""

    # Return a failure for an invalid request
    try:
        to_un = request.form['to_un']
        from_un = request.form['from_un']
        msg = request.form['msg']
    except Exception as e:
        return jsonify(
            dict(status='failure', reason=str(e))
        ), 400

    # Query for the sending and receiving users
    to_user = db.session.query(User).filter(User.username == to_un).first()
    from_user = db.session.query(User).filter(User.username == from_un).first()

    # Write the message to the DB if both users exist
    if to_user and from_user:
        db.session.add(
            PendingMessage(
                to_user_id=to_user.id, from_user_id=from_user.id, message=msg
            )
        )
        db.session.commit()
        return jsonify(dict(status='success', msg=msg)), 200
    else:
        return jsonify(dict(status='failure', reason='user not found')), 403


@bp.route('/get_msg', methods=['POST'])
def get_msg():
    """Get text messages from a given user."""

    # Return a failure for an invalid request
    try:
        to_un = request.form['to_un']
        from_un = request.form['from_un']
    except Exception as e:
        return jsonify(
            dict(status='failure', reason=str(e))
        ), 400

    # Query for the sending and receiving users
    to_user = db.session.query(User).filter(User.username == to_un).first()
    from_user = db.session.query(User).filter(User.username == from_un).first()

    # Read the pending messages from the DB if both users exist
    if to_user and from_user:
        pending = db.session.query(PendingMessage).filter(
            and_(
                PendingMessage.from_user_id == from_user.id,
                PendingMessage.to_user_id == to_user.id
            )
        )
        msgs = [row.message for row in pending]
        # Delete the messages after reading them
        for row in pending:
            db.session.delete(row)
        db.session.commit()

        return jsonify(dict(status='success', msgs=msgs)), 200
    else:
        return jsonify(dict(status='failure', reason='user not found')), 403


@bp.route('/health_check', methods=['GET', 'POST'])
def health_check():
    """Returns a simple JSON response if the app is online."""

    app.logger.debug('API call to /show_pending')

    return jsonify(dict(status='success')), 200
