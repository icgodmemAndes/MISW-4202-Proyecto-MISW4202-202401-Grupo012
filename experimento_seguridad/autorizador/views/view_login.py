import datetime

from marshmallow import ValidationError
from flask import request
from flask_restful import Resource

from events.trace_event import TraceEvent
from models import User, UserSchema, db
from marshmallow import ValidationError
from flask_jwt_extended import create_access_token

users_schema = UserSchema()


class ViewLogin(Resource):

    #ctor
    def __init__(self):
        self.trace_event = TraceEvent(db)

    def post(self):
        try:
            print('[POST] data: {}'.format(str(request.json)))
            users = users_schema.load(request.json, session=db.session)

            # Check if user exists
            user = User.query.filter_by(username=users.username).first()

            if user is None:
                self.trace_event.save('login', 'User not found')    
                return {'message': 'Cannot complete authentication process'}, 401
            
            if user.password != users.password:
                self.trace_event.save('login', 'Invalid password')
                return {'message': 'Cannot complete authentication process'}, 401
            
            if user.is_blocked:
                self.trace_event.save('login', 'User blocked')
                return {'message': 'User has been blocked'}, 401
            
            self.trace_event.save('login', 'User authenticated')
            access_token = create_access_token(identity={"user_id" : user.user_id, "roles" : user.roles }, expires_delta=datetime.timedelta(hours=1))
            
            return {'message': 'User authenticated', 'token': access_token}, 200

        except ValidationError as e:
            return e.messages, 400
