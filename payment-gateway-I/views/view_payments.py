import datetime

from marshmallow import ValidationError
from flask import request
from flask_restful import Resource
from models import Payment, PaymentSchema, db
from payments.payment_processor import PaymentProcessor
from marshmallow import ValidationError

payment_schema = PaymentSchema()


class ViewPayments(Resource):

    def post(self):
        try:
            print('[POST] data: {}'.format(str(request.json)))
            payment = payment_schema.load(request.json, session=db.session)
            payment_processor = PaymentProcessor(db)
            if payment.is_retry:
                return payment_processor.retry_payment(db, payment)
            return payment_processor.process_payment(db, payment)
        except ValidationError as e:
            return e.messages, 400
