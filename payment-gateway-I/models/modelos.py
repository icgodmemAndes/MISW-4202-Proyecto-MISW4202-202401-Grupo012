from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()

class ServiceStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(25), nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.String(100), nullable=False)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(100), nullable=False)
    gateway = db.Column(db.Integer, nullable=False)
    is_retry = db.Column(db.Boolean, nullable=False)


class PaymentSchema(SQLAlchemyAutoSchema):    
    class Meta:
        model = Payment
        load_instance = True
