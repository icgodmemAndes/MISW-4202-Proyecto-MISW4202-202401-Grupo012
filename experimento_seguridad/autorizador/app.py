import os
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from views.view_login import ViewLogin
from models import db
from flask_jwt_extended import JWTManager

bd_path = os.environ.get('BD_PATH', 'sqlite:///identity.db')


def create_flask_app():
    _app = Flask(__name__)
    _app.config['SQLALCHEMY_DATABASE_URI'] = bd_path
    _app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    _app.config['JWT_SECRET_KEY'] = os.environ.get('PHRASE_SECRET', 'local')
    _app.config['PROPAGATE_EXCEPTIONS'] = True

    jwt = JWTManager(_app)

    app_context = _app.app_context()
    app_context.push()
    add_urls(_app)
    CORS(
        _app,
        origins="*",
    )
    return _app


def add_urls(_app):
    api = Api(_app)
    api.add_resource(ViewLogin, '/login')


app = create_flask_app()
db.init_app(app)
db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 6000), debug=False)
