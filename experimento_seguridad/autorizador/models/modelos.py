from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()

class User(db.Model):
    __table_args__ = (UniqueConstraint('username', name='unique_username'),)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    roles = db.Column(db.String(150), nullable=True)
    is_blocked = db.Column(db.Boolean(50), nullable=False, default=False)


class InvalidAttemps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=True, default=db.func.current_timestamp())
    failed_attemps = db.Column(db.Integer(), nullable=True, default=0)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.String(100), nullable=False)


class UserSchema(SQLAlchemyAutoSchema):    
    class Meta:
        model = User
        load_instance = True
