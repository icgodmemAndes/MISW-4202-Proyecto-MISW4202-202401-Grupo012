import datetime

from marshmallow import ValidationError
from flask import request
from flask_restful import Resource
from attemps.attemps_handler import AttempsHandler
from events.trace_event import TraceEvent
from models import User, UserSchema, db
from marshmallow import ValidationError
from flask_jwt_extended import current_user, jwt_required

users_schema = UserSchema()


class ViewValidate(Resource):

    #ctor
    def __init__(self):
        self.trace_event = TraceEvent(db)
        self.attemp_handler = AttempsHandler(db)

    @jwt_required()
    def get(self):
        try:
            user = User.query.filter_by(user_id=int(current_user)).one_or_none()

            if user is None:
                return {'message': 'Not authorized', 'code': 1}, 401
            if user.is_blocked:
                return {'message': 'Not authorized', 'code': 2}, 401
            return {'message': 'Authorized', }, 200
        except:
            return {'message': 'Not authorized', 'code': 3}, 401

