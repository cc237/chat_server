from bcrypt import gensalt, hashpw
from flask import current_app as app, jsonify, request
from sqlalchemy import and_
from sqlalchemy.sql import exists

from app.blueprints import bp
from app.extensions import db
from app.models import Friend, PendingMessage, User


# TODO: Need to have voice and image messaging
# TODO: Write generic function to validate the request parameters
# TODO: Remove the "show_pending" route


@bp.route('/get_friends', methods=['POST'])
def get_friends():
    """Returns all friends of a given user."""

    # Return a failure for an invalid request
    try:
        un = request.form['un']
    except Exception as e:
        return jsonify(
            dict(status='failure', friends_found=False, reason=str(e))
        ), 400

    # Query for the user
    user = db.session.query(User).filter(User.username == un).first()

    if user:
        return jsonify(
            dict(status='success', users=[f.friend_name for f in user.friends])
        ), 200
    else:
        return jsonify(
            dict(status='failure', friends_found=False, reason='invalid user')
        ), 401


@bp.route('/add_friend', methods=['POST'])
def add_friend():
    """Add a friend for a given user."""

    # Return a failure for an invalid request
    try:
        un = request.form['un']
        friend_un = request.form['friend_un']
    except Exception as e:
        return jsonify(
            dict(status='failure', friend_added=False, reason=str(e))
        ), 400

    # Query for the user and the friend
    user = db.session.query(User).filter(User.username == un).first()
    friend = db.session.query(User).filter(User.username == friend_un).first()

    # Add the friend if both users are valid and the friend doesn't exist
    if user and friend:
        friendship = db.session.query(Friend).filter(
            and_(
                Friend.user_id == user.id,
                Friend.friend_name == friend_un
            )
        ).first()
        if not friendship:
            db.session.add(Friend(user_id=user.id, friend_name=friend_un))
            db.session.commit()
            return jsonify(
                dict(
                    status='success',
                    friend_added=True,
                    reason='valid new friend'
                )
            ), 200
        else:
            return jsonify(
                dict(
                    status='failure',
                    friend_added=False,
                    reason='friendship already exists'
                )
            ), 403
    else:
        return jsonify(
            dict(
                status='failure',
                friend_added=False,
                reason='user or friend not found'
            )
        ), 403


@bp.route('/remove_friend', methods=['POST'])
def remove_friend():
    """Remove a friend for a given user."""

    # Return a failure for an invalid request
    try:
        un = request.form['un']
        friend_un = request.form['friend_un']
    except Exception as e:
        return jsonify(
            dict(status='failure', friend_removed=False, reason=str(e))
        ), 400

    # Query for the user and the friend
    user = db.session.query(User).filter(User.username == un).first()
    friend = db.session.query(User).filter(User.username == friend_un).first()

    # Remove the friend if both users are valid and the friend exists
    if user and friend:
        friendship = db.session.query(Friend).filter(
            and_(
                Friend.user_id == user.id,
                Friend.friend_name == friend_un
            )
        ).first()
        if friendship:
            user.friends.remove(friendship)
            db.session.commit()
            return jsonify(
                dict(
                    status='success',
                    friend_removed=True,
                    reason='valid friend removed'
                )
            ), 200
        else:
            return jsonify(
                dict(
                    status='failure',
                    friend_removed=False,
                    reason='friend not found'
                )
            ), 403
    else:
        return jsonify(
            dict(
                status='failure',
                friend_removed=False,
                reason='user or friend not found'
            )
        ), 403


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

    # Check if the user already exists. If not, register them. Otherwise,
    # return a failure indicating that the user exists.
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

    app.logger.debug('API call to /health_check')

    return jsonify(dict(status='success')), 200
