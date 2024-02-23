from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from views.view_ping import ViewPing
from views.view_payments import ViewPayments
from models import db, Payment, PaymentSchema


app = None


def create_flask_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payments.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
    app.config['PROPAGATE_EXCEPTIONS'] = True

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
    api.add_resource(ViewPayments, '/execute_payment')
    api.add_resource(ViewPing, '/ping')


app = create_flask_app()
db.init_app(app)
db.create_all()

if __name__ == '__main__':
    app.run(port=6000, debug=True)
