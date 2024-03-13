import enum
from sqlalchemy import UniqueConstraint
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()


class PlanType(enum.Enum):
    BASIC = "BASIC"
    PREMIUM = "PREMIUM"


class User(db.Model):
    __table_args__ = (UniqueConstraint('email', name='unique_email'),)
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    plan = db.Column(db.Enum(PlanType), nullable=False)


class Event(db.Model):
    __table_args__ = ()
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False)


class UserSchema(SQLAlchemyAutoSchema):
    plan = fields.Enum(PlanType, by_value=True, allow_none=False)

    class Meta:
        model = User
        load_instance = True


class EventSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        load_instance = True
