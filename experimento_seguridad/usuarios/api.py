import os
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_restful import Resource
from models import db


class HealthSource(Resource):

    @staticmethod
    def get():
        return {'status': 'ok'}


class ProfileSource(Resource):

    @staticmethod
    def get():
        return {'status': 'ok'}


def add_urls(_app):
    api = Api(_app)
    api.add_resource(HealthSource, '/')
    api.add_resource(ProfileSource, '/profile')


def create_flask_app():
    _app = Flask(__name__)
    _app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('BD_PATH', 'sqlite:///users.db')
    _app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    _app.config['PROPAGATE_EXCEPTIONS'] = True

    app_context = _app.app_context()
    app_context.push()
    add_urls(_app)
    CORS(_app, origins="*")

    return _app


app = create_flask_app()
db.init_app(app)
db.create_all()

if __name__ == '__main__':
    print('[Users] Running')
    app.run(
        debug='{}'.format(os.environ.get('DEBUG', False)).lower() == 'true',
        host='0.0.0.0',
        port=os.environ.get('PORT', 6000)
    )
