import os
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from views.view_login import ViewLogin
from models import db
from flask_jwt_extended import JWTManager

bd_path = os.environ.get('BD_PATH', 'sqlite:///identity.db')

app = None


def create_initial_data():
    from models import User
    user1 = User(username='admin', password='admin123!@#', user_id=1, roles='admin, user')
    user2 = User(username='username', password='password', user_id=2,  roles='user')
    user3 = User(username='guest', password='password', user_id=3, roles='guest')
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.commit()

def create_flask_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = bd_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
    app.config['JWT_SECRET_KEY'] = os.environ.get('PHRASE_SECRET', 'local')
    app.config['PROPAGATE_EXCEPTIONS'] = True

    jwt = JWTManager(app)

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



app = create_flask_app()
db.init_app(app)
db.create_all()
create_initial_data()



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 6000), debug=False)
