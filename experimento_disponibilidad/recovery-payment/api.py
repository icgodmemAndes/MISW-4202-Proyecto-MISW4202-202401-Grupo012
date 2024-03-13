from flask import Flask, request, Response
from flask_restful import Api, Resource
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
r = redis.StrictRedis(host=redis_host, port=redis_port, db=0, charset='utf-8', decode_responses=True)

# ActiveMQ configuration
host = os.environ.get('HOST_QUEUE', 'localhost')
port = os.environ.get('PORT_QUEUE', 61613)
hosts = [(host, port)]
queue_name_one = os.environ.get('QUEUE_NAME_ONE', 'one')
queue_name_two = os.environ.get('QUEUE_NAME_TWO', 'two')

api = Api(app)

current_payment_gateway_status = {
    "payment_gate_way_one": "",
    "payment_gate_way_two": "",
}

hostOne = os.environ.get('HOST_GATEWAY_ONE', 'http://localhost:6001')
hostTwo = os.environ.get('HOST_GATEWAY_TWO', 'http://localhost:6002')


# ActiveMQ Listener
class PaymentListener(stomp.ConnectionListener):
    def on_error(self, frame):
        print('received an error "%s"' % frame.body)

    def on_message(self, frame):
        with app.app_context():
            print('[on_message] Processing new messages: {}'.format(frame.body))
            message_translated = json.loads(frame.body.replace("'", '"'))
            r.set('{}.{}'.format(message_translated['gateway'], message_translated['id']), frame.body)


def active_mq_listener():
    conn = stomp.Connection(host_and_ports=hosts)
    conn.set_listener('', PaymentListener())
    # conn.start()
    conn.connect('admin', 'admin', wait=True)
    conn.subscribe(destination=queue_name_one, id=1, ack='auto')
    conn.subscribe(destination=queue_name_two, id=2, ack='auto')
    print(f"Subscribed to ActiveMQ queue: {queue_name_one}")
    print(f"Subscribed to ActiveMQ queue: {queue_name_two}")

    while True:
        time.sleep(1)  # Keep the thread alive


# Redis Subscriber
def topic_stream():
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
                    # Reprocess payment
                process_payments()


def process_payments():
    if current_payment_gateway_status['payment_gate_way_one'] == 'up':
        keys = r.keys("one.*")
        print(keys)
        for key in keys:
            message = r.get(key)
            payment = json.loads(message.replace("'", '"'))
            payment['is_retry'] = True
            response = requests.post(f"{hostOne}/execute_payment", json=payment)
            if response.status_code == 200:
                r.delete(key)
                print('[on_stream] PaymentOne processed: -> {%s:%s}' % (payment['id'], payment['value']))
    if current_payment_gateway_status['payment_gate_way_two'] == 'up':
        keys = r.keys("two.*")
        for key in keys:
            message = r.get(key)
            payment = json.loads(message.replace("'", '"'))
            payment['is_retry'] = True
            response = requests.post(f"{hostTwo}/execute_payment", json=payment)
            if response.status_code == 200:
                r.delete(key)
                print('[on_stream] PaymentTwo processed -> {%s:%s}' % (payment['id'], payment['value']))


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
    # Start Redis subscriber and ActiveMQ listener in separate threads
    redis_thread = threading.Thread(target=topic_stream, daemon=True)
    redis_thread.start()

    active_mq_thread = threading.Thread(target=active_mq_listener, daemon=True)
    active_mq_thread.start()

    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=False)
