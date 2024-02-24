from flask import Flask, request, Response
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import redis
import stomp
import datetime
import json
import threading
import time
import requests
import os

app = Flask(__name__)
# Redis Configuration
redis_host = os.environ.get('HOST_REDIS', 'localhost')
redis_port = os.environ.get('PORT_REDIS', 6379)
redis_topic_name = os.environ.get('TOPIC_HEALTH', 'payment_gateway_status')

# ActiveMQ configuration
host = os.environ.get('HOST_QUEUE', 'localhost')
port = os.environ.get('PORT_QUEUE', 61613)
hosts = [(host, port)]
queue_name_one = os.environ.get('QUEUE_NAME_ONE', 'one')
queue_name_two = os.environ.get('QUEUE_NAME_TWO', 'two')

conn = stomp.Connection(host_and_ports=hosts)

bd_path = os.environ.get('BD_PATH', 'sqlite:///recovery.db')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = bd_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)

current_payment_gateway_status = {
    "payment_gate_way_one": "",
    "payment_gate_way_two": "",
}

hostOne = os.environ.get('HOST_GATEWAY_ONE', 'http://localhost:6001')
hostTwo = os.environ.get('HOST_GATEWAY_TWO', 'http://localhost:6002')


# Models payment
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)
    gateway = db.Column(db.String(100), nullable=False)
    is_retry = db.Column(db.Boolean, nullable=True, default=False)
    processed = db.Column(db.Boolean, nullable=True, default=False)


class PaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ("id", "value", "gateway", "is_retry", "processed")


payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)


# Models health status
class Health(db.Model):
    component = db.Column(db.String(100), primary_key=True)
    status = db.Column(db.String(100), nullable=False)


class HealthSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ("component", "status")


health_schema = HealthSchema()
healths_schema = HealthSchema(many=True)


# ActiveMQ Listener
class PaymentListener(stomp.ConnectionListener):
    def on_error(self, frame):
        print('received an error "%s"' % frame.body)

    def on_message(self, frame):
        with app.app_context():
            print('[on_message] Processing new messages: {}'.format(frame.body))
            message_translated = json.loads(frame.body.replace("'", '"'))
            new_payment = Payment(
                id=message_translated['id'],
                value=message_translated['value'],
                gateway=message_translated['gateway'],
                is_retry=message_translated.get('is_retry', False),
                processed=False,
            )
            #db.session.add(new_payment)
            #db.session.commit()
            process_payments(new_payment)
            print('NOTIFY PENDING PAYMENT RECEIVED -> {%s:%s:%s}' % (
                new_payment.id, new_payment.gateway, new_payment.value))


def active_mq_listener():
    conn.set_listener('', PaymentListener())
    conn.connect('admin', 'admin', wait=True)
    #conn.subscribe(destination=queue_name_one, id=1, ack='auto')
    #conn.subscribe(destination=queue_name_two, id=2, ack='auto')
    #print(f"Subscribed to ActiveMQ queue: {queue_name_one}")
    #print(f"Subscribed to ActiveMQ queue: {queue_name_two}")

    while True:
        time.sleep(1)  # Keep the thread alive


# Redis Subscriber
def topic_stream():
    r = redis.StrictRedis(host=redis_host, port=redis_port, db=0, charset='utf-8', decode_responses=True)
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(redis_topic_name)

    print(f"Subscribed to Redis topic: {redis_topic_name}")
    # TODO: handle client disconnection.
    for message in pubsub.listen():
        with app.app_context():
            print(message)
            if message['type'] == 'message':
                print(f"Received message from Redis topic: {message['data']}")
                raw_data = message['data'].replace("'", '"')
                healthStatus = json.loads(raw_data)
                if 'payment_gate_way_one' in healthStatus:
                    current_payment_gateway_status['payment_gate_way_one'] = healthStatus['payment_gate_way_one']
                elif 'payment_gate_way_two' in healthStatus:
                    current_payment_gateway_status['payment_gate_way_two'] = healthStatus['payment_gate_way_two']
                
                handle_subscribe()
                


def mapper_to_gateway(payment):
    return {
        'id': payment.id,
        'value': payment.value,
        'gateway': payment.gateway,
        'is_retry': payment.is_retry,
    }

def handle_subscribe():
    if current_payment_gateway_status['payment_gate_way_one'] == 'up':
        conn.subscribe(destination=queue_name_one, id=1, ack='auto')
        print(f"Subscribed to ActiveMQ queue: {queue_name_one}")
    elif current_payment_gateway_status['payment_gate_way_one'] == 'down':
        try:
            conn.unsubscribe(id=1)
            print(f"Unsubscribed from ActiveMQ queue: {queue_name_one}")
        except NameError:
            print(f"Unknown subscription to ActiveMQ queue: {queue_name_one}")
        
    if current_payment_gateway_status['payment_gate_way_two'] == 'up':
        conn.subscribe(destination=queue_name_two, id=2, ack='auto')
        print(f"Subscribed to ActiveMQ queue: {queue_name_two}")
    elif current_payment_gateway_status['payment_gate_way_two'] == 'down':
        try:
            conn.unsubscribe(id=2)
            print(f"Unsubscribed from ActiveMQ queue: {queue_name_two}")
        except NameError:
            print(f"Unknown subscription to ActiveMQ queue: {queue_name_two}")

def process_payments(payment):
    if current_payment_gateway_status['payment_gate_way_one'] == 'up' and payment.gateway == 'one':
        #unproccesed_payment_one = Payment.query.filter(Payment.gateway == 'one', Payment.processed == False).all()
        #for payment in unproccesed_payment_one:
        payment.is_retry = True
        response = requests.post(f"{hostOne}/execute_payment", json=payment_schema.dump(mapper_to_gateway(payment)))
        if response.status_code == 200:
            payment.processed = True
            #db.session.add(payment)
            #db.session.commit()
            print('NOTIFY PAYMENT_GATEWAY_ONE PROCESSED -> {%s:%s}' % (payment.id, payment.value))
    if current_payment_gateway_status['payment_gate_way_two'] == 'up' and payment.gateway == 'two':
        #unproccesed_payment_two = Payment.query.filter(Payment.gateway == 'two', Payment.processed == False).all()
        #for payment in unproccesed_payment_two:
        payment.is_retry = True
        response = requests.post(f"{hostTwo}/execute_payment", json=payment_schema.dump(mapper_to_gateway(payment)))
        if response.status_code == 200:
            payment.processed = True
            #db.session.commit()
            #db.session.commit()
            print('NOTIFY PAYMENT_GATEWAY_TWO PROCESSED -> {%s:%s}' % (payment.id, payment.value))


class TestPublishResource(Resource):
    def post(self):
        message = request.data.decode('UTF-8')
        now = datetime.datetime.now().replace(microsecond=0).time()
        print('to redis')
        print('[%s]: %s' % (now.isoformat(), message))
        redis_conn = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
        redis_conn.publish(redis_topic_name, str(message))
        return Response(status=204)


api.add_resource(TestPublishResource, '/publish')

if __name__ == '__main__':
    # Create the database tables
    with app.app_context():
        db.create_all()

    # Start Redis subscriber and ActiveMQ listener in separate threads
    redis_thread = threading.Thread(target=topic_stream, daemon=True)
    redis_thread.start()

    active_mq_thread = threading.Thread(target=active_mq_listener, daemon=True)
    active_mq_thread.start()

    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=False)
