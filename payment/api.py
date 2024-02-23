import os
import stomp
import redis
import requests
import time
import json
from faker import Faker
from flask import Flask, request
from flask_restful import Api, Resource

faker = Faker()

app = Flask(__name__)
app_context = app.app_context()
app_context.push()
api = Api(app)

hostRedis = os.environ.get('HOST_REDIS', 'localhost')
portRedis = os.environ.get('PORT_REDIS', 6379)

topicHealth = 'gateWayHealth'

hostQueue = os.environ.get('HOST_QUEUE', 'localhost')
portQueue = os.environ.get('PORT_QUEUE', 61613)
userQueue = 'admin'
passQueue = 'admin'
clientQueue = 'paymentQueue'
hostsQueue = [(hostQueue, portQueue)]

hostGatewayOne = os.environ.get('HOST_GATEWAY_ONE', 'http://localhost:6001')
hostGatewayTwo = os.environ.get('HOST_GATEWAY_TWO', 'http://localhost:6002')

queueNameOne = os.environ.get('QUEUE_NAME_ONE', 'one')
queueNameTwo = os.environ.get('QUEUE_NAME_TWO', 'two')

statusGateways = {}
statusError = 'error'
statusDone = 'done'


def redis_read(message):
    print('[Redis] new message: {0}'.format(message))

    if message['type'] == 'message' and message['data'] is not None:
        event = json.loads(message['data'].replace("'", '"'))
        statusGateways[event['gateway']] = event['value']
        print('[Redis] changed gateway status: {0}'.format(statusGateways))


def redis_subscribe():
    print('[Redis] Starting listener')
    pubsub = _redis.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(**{topicHealth: redis_read})
    pubsub.run_in_thread(sleep_time=0.001)


def stomp_connect(_conn):
    _conn.connect(userQueue, passQueue, wait=True, headers={'client-id': clientQueue})
    print('[Queue] New Connection')


def stomp_send(body, queue_name):
    print('[Queue] STARTING ENQUEUEING TO {0}'.format(queue_name))
    conn.send(
        body=str(body),
        destination='/queue/{0}'.format(queue_name),
        persistent=True,
        headers={'persistent': "true"},
    )
    print('[Queue] Send new payment failed')


class ConnectionListener(stomp.ConnectionListener):
    def __init__(self, _conn):
        self._conn = _conn

    @staticmethod
    def on_error(message):
        print('[Queue] received an error "%s"' % message)

    def on_disconnected(self):
        print('[Queue] Queue disconnected')
        stomp_connect(self._conn)


def request_to(body, gateway_name, queue_name, host_name):
    print('[REQUEST] to {0}'.format(gateway_name))
    try:
        response = requests.post('{0}/execute_payment'.format(host_name), data=body)

        if response.status_code == 200:
            result = {'error': '', 'details': response.json(), 'status': 'done'}
        else:
            stomp_send(body, queue_name)
            result = {'error': '', 'details': response.json(), 'status': 'queueing'}

        return {'result': result, 'gateway': gateway_name}
    except Exception as ex:
        print('[REQUEST] [{0}] throw error {1}'.format(gateway_name, str(ex)))
        stomp_send(body, queue_name)
        # Only Internal Payment Test
        # _redis.publish(topicHealth, str(body))

        return {'result': {'error': str(ex), 'details': {}, 'status': 'pending'}, 'gateway': gateway_name}


def request_queue(body, gateway_name, queue_name):
    print('[REQUEST] direct to queue {0}'.format(gateway_name))
    stomp_send(body, queue_name)

    return {
        'result': {'error': '', 'details': {gateway_name: statusGateways[gateway_name]}, 'status': 'pending'},
        'gateway': gateway_name
    }


def request_generate(body):
    is_one = body['gateway'] == 'one'
    gateway_name = body['gateway']
    queue_name = queueNameOne if is_one else queueNameTwo
    host_name = hostGatewayOne if is_one else hostGatewayTwo

    print('[REQUEST] current status {}'.format(statusGateways))

    if statusGateways.get(gateway_name, None) is None or statusGateways.get(gateway_name) == statusDone:
        response = request_to(body, gateway_name, queue_name, host_name)
    else:
        response = request_queue(body, gateway_name, queue_name)

    return response


class HealthSource(Resource):

    @staticmethod
    def get():
        return {'status': 'ok'}


class PaymentResource(Resource):

    @staticmethod
    def post():
        payment = request.json
        print('[Http] Starting request, {0}'.format(str(payment)))

        if payment.get('gateway', None) is None or payment.get('value', None) is None:
            return {
                'result': {'error': 'data incomplete', 'details': {}, 'status': 'invalid'},
                'gateway': 'unknown'
            }, 400

        gateway = payment.get('gateway')

        if gateway != 'one' and gateway != 'two':
            return {
                'result': {'error': 'gateway invalid', 'details': {}, 'status': 'invalid'},
                'gateway': 'unknown'
            }, 400

        response = request_generate({
            'id': int(faker.unique.aba()),
            'gateway': gateway,
            'value': payment.get('value'),
        })
        print('[Http] Ended request, {0}'.format(str(response)))

        return response, 200


_redis = redis.StrictRedis(hostRedis, portRedis, 0, charset='utf-8', decode_responses=True)

conn = stomp.Connection(host_and_ports=hostsQueue)
conn.set_listener('list', ConnectionListener(conn))

api.add_resource(HealthSource, '/health')
api.add_resource(PaymentResource, '/payment')

if __name__ == '__main__':
    redis_subscribe()
    stomp_connect(conn)
    time.sleep(1)
    print('[Api] Running')
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 6000))
