import datetime

from marshmallow import ValidationError
from flask import request
from flask_restful import Resource
from attemps.attemps_handler import AttempsHandler
from events.trace_event import TraceEvent
from models import User, UserSchema, db
from marshmallow import ValidationError
from flask_jwt_extended import create_access_token

users_schema = UserSchema()


class ViewLogin(Resource):

    # ctor
    def __init__(self):
        self.trace_event = TraceEvent(db)
        self.attemp_handler = AttempsHandler(db)

    def post(self):
        try:
            users = users_schema.load(request.json, session=db.session)

            if users.username is None or users.username == "" or users.password is None or users.password == "":
                return {'message': 'data missing'}, 401

            # Check if user exists
            user = User.query.filter_by(username=users.username).one_or_none()

            if user is None:
                self.trace_event.save('login', 'User not found')
                self.attemp_handler.register_invalid_attemp(users.username)
                return {'message': 'Cannot complete authentication process'}, 401

            current_attemps = self.attemp_handler.get_attemps(users.username)

            if current_attemps >= 3:
                self.trace_event.save('login', 'User has been blocked')
                self.block_user(users.username)

            if user.is_blocked:
                self.trace_event.save('login', 'User blocked')
                return {'message': 'User has been blocked'}, 401

            if user.password != users.password:
                self.trace_event.save('login', 'Invalid password')
                self.attemp_handler.register_invalid_attemp(users.username)
                return {'message': 'Cannot complete authentication process'}, 401

            self.trace_event.save('login', 'User authenticated')
            self.attemp_handler.reset_attemps(users.username)
            access_token = create_access_token(identity={"user_id": user.user_id, "roles": user.roles},
                                               expires_delta=datetime.timedelta(hours=1))

            return {'message': 'User authenticated', 'token': access_token}, 200

        except ValidationError as e:
            return e.messages, 400

    def block_user(self, username):
        user = User.query.filter_by(username=username).first()
        if user is not None:
            user.is_blocked = True
            db.session.add(user)
            db.session.commit()
            return user.id
        else:
            return None
