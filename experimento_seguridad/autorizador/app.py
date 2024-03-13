import os
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from views.view_login import ViewLogin
from views.view_validate import ViewValidate
from models import db
from flask_jwt_extended import JWTManager

bd_path = os.environ.get('BD_PATH', 'sqlite:///identity.db')

app = None


def create_initial_data():
    from models import User


def create_flask_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = bd_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
    app.config['JWT_SECRET_KEY'] = os.environ.get('PHRASE_SECRET', 'local')
    app.config['PROPAGATE_EXCEPTIONS'] = True

    jwt = JWTManager(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data['sub']
        return identity['user_id']

    app_context = app.app_context()
    app_context.push()
    add_urls(app)
    CORS(
        app,
        origins="*",
    )
    return app


def add_urls(app):
    api = Api(app)
    api.add_resource(ViewLogin, '/login')
    api.add_resource(ViewValidate, '/validate_token')



    

app = create_flask_app()
db.init_app(app)
db.create_all()
create_initial_data()



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 6000), debug=False)
