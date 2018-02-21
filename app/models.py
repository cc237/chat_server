"""All SQL Alchemy models are defined here."""

from sqlalchemy import UniqueConstraint

from app.extensions import db


class Friend(db.Model):
    """Friend table model"""

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey('user.id'))
    friend_name = db.Column(db.String(32))
    user = db.relationship('User', back_populates='friends')

    __table_args__ = (UniqueConstraint('user_id', 'friend_name'), {})


class User(db.Model):
    """User table model"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    pw_hash = db.Column(db.Binary(64), nullable=False)
    friends = db.relationship(
        'Friend', back_populates='user', cascade='all, delete-orphan'
    )


class PendingMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(256), nullable=False)
