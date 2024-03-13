import os
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_restful import Resource
from flask_jwt_extended import JWTManager
from flask_jwt_extended import current_user, jwt_required
from models import db, UserSchema, create_event, get_user

user_schema = UserSchema()

roles_valid = ['basic_user', 'premium_user', 'full_access']

class HealthSource(Resource):

    @staticmethod
    def get():
        return {'status': 'ok'}


class ProfileSource(Resource):

    @staticmethod
    @jwt_required()
    def get():
        token = current_user
        user_id = token['user_id']

        if token['roles'] is None or token['roles'] not in roles_valid:
            create_event('do_not_have_roles', '{}'.format(token['roles']), None if user_id is None else user_id)
            return {'error': 'Not authorized', 'code': 1}, 401

        if user_id is None or not isinstance(user_id, int):
            create_event('do_not_have_user_id', '{}'.format(user_id), None)
            return {'error': 'Not authorized', 'code': 2}, 401

        user = get_user(int(user_id))

        if user is None:
            create_event('user_does_not_exists', '', user_id)
            return {'error': 'Not authorized', 'code': 3}, 401

        create_event('profile_success', '', user_id)

        return user_schema.dump(user), 200


def add_urls(_app):
    api = Api(_app)
    api.add_resource(HealthSource, '/')
    api.add_resource(ProfileSource, '/profile')


def create_flask_app():
    _app = Flask(__name__)
    _app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('BD_PATH', 'sqlite:///users.db')
    _app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    _app.config['PROPAGATE_EXCEPTIONS'] = True
    _app.config['JWT_SECRET_KEY'] = os.environ.get('PHRASE_SECRET', 'local')

    app_context = _app.app_context()
    app_context.push()
    add_urls(_app)
    CORS(_app, origins="*")

    jwt = JWTManager(_app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data['sub']
        user_id = identity['user_id']
        roles = '{}'.format(identity['roles'])
        data = {'user_id': user_id, 'roles': roles}

        return data

    return _app


app = create_flask_app()
db.init_app(app)
db.create_all()

if __name__ == '__main__':
    print('[Users] Running')
    app.run(
        debug='{}'.format(os.environ.get('DEBUG', True)).lower() == 'true',
        host='0.0.0.0',
        port=os.environ.get('PORT', 6000)
    )
