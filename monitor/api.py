import requests
from flask import Flask
from flask_restful import Api, Resource
import datetime
import redis
import os
import threading

hostRedis = os.environ.get('HOST_REDIS', 'localhost')
portRedis = os.environ.get('PORT_REDIS', 6379)

delayInterval = int(os.environ.get('DELAY_INTERVAL', 15))
topicHealth = os.environ.get('TOPIC_HEALTH', 'payment_gateway_status')

app = Flask(__name__)
app_context = app.app_context()
app_context.push()
api = Api(app)

r = redis.StrictRedis(hostRedis, portRedis, 0, charset='utf-8', decode_responses=True)

current_payment_gateway_status = {
    "payment_gate_way_one": "",
    "payment_gate_way_two": "",
}

hosts_payment_gateway = {
    "payment_gate_way_one": os.environ.get('HOST_GATEWAY_ONE', 'http://localhost:6000'),
    "payment_gate_way_two": os.environ.get('HOST_GATEWAY_TWO', 'http://localhost:6002'),
}


def execute_ping_to_payment_gateways():
    now = datetime.datetime.now().replace(microsecond=0).time()
    print('+-------START EXECUTION JOB SCHEDULER [%s]-------+' % now.isoformat(timespec='microseconds'))

    for payment_gateway in current_payment_gateway_status:
        make_ping_to_payment_gateway(payment_gateway)

    now = datetime.datetime.now().replace(microsecond=0).time()
    print('+-------END EXECUTION JOB SCHEDULER [%s]-------+' % now.isoformat(timespec='microseconds'))
    print('[Execute Ping] result {}'.format(str(current_payment_gateway_status)))


def make_ping_to_payment_gateway(payment_gateway_name):
    try:
        payment_gateway_status_response = requests.get(f"{hosts_payment_gateway[payment_gateway_name]}/ping?echo=up")
        response_text = payment_gateway_status_response.text.replace('\n', '').replace('"','')
        print('[Response {}] is *{}*'.format(payment_gateway_name, response_text))
        response_text = response_text if response_text == 'up' else 'down'

        if payment_gateway_status_response.status_code == 200 and current_payment_gateway_status[
            payment_gateway_name] != response_text:
            notify_payment_gateway_status(payment_gateway_name, response_text)

        elif payment_gateway_status_response.status_code != 200:
            notify_payment_gateway_status(payment_gateway_name, "down")

    except:
        if current_payment_gateway_status[payment_gateway_name] != "down":
            notify_payment_gateway_status(payment_gateway_name, "down")


def notify_payment_gateway_status(payment_gateway, new_payment_gateway_status):
    current_status_pg = current_payment_gateway_status[payment_gateway]

    try:
        message = {payment_gateway: new_payment_gateway_status}
        current_payment_gateway_status[payment_gateway] = new_payment_gateway_status

        r.publish(topicHealth, str(message))
        print('NOTIFY PAYMENT_GATEWAY CHANGE STATE (%s) -> {%s:%s}' % (
            topicHealth, payment_gateway, new_payment_gateway_status
        ))

    except Exception as ex:
        print('[Notify Status] error {}'.format(str(ex)))
        current_payment_gateway_status[payment_gateway] = current_status_pg


def repeat_task():
    threading.Timer(0.5, execute_ping_to_payment_gateways).start()
    threading.Timer(delayInterval, repeat_task).start()


class MonitorHealthResource(Resource):
    def get(self):
        return {"status": "up!"}


class PaymentGatewayHealthResource(Resource):
    def get(self, payment_gateway_name):
        make_ping_to_payment_gateway(payment_gateway_name)
        return {}


api.add_resource(MonitorHealthResource, '/monitor/health-check')
api.add_resource(PaymentGatewayHealthResource, '/monitor/test-ping/<string:payment_gateway_name>')

if __name__ == '__main__':
    threading.Timer(5, repeat_task).start()
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5003))
