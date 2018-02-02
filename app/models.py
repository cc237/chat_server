"""All SQL Alchemy models are defined here."""

from app.extensions import db


class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(
        'User', back_populates='friends', foreign_keys=[user_id]
    )


class User(db.Model):
    """User table model"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    pw_hash = db.Column(db.Binary(64), nullable=False)
    friends = db.relationship(
        'Friend', back_populates='user', foreign_keys=[Friend.friend_id]
    )


class PendingMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(256), nullable=False)
