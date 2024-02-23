import sched
import time
import requests
from flask import Flask
from flask_restful import Api, Resource
import datetime
import redis

app = Flask(__name__)
app_context = app.app_context()
app_context.push()
api = Api(app)

r = redis.StrictRedis('localhost', 6379, 0, charset='utf-8', decode_responses=True)

current_payment_gateway_status = {
    "payment_gate_way_one": "",
    "payment_gate_way_two": "",
}

def execute_ping_to_payment_gateways():
    now = datetime.datetime.now().replace(microsecond=0).time()
    print('+-------START EXECUTION JOB SCHEDULER [%s]-------+' % now.isoformat(timespec='microseconds'))

    for payment_gateway in current_payment_gateway_status:
        make_ping_to_payment_gateway(payment_gateway)
    
    now = datetime.datetime.now().replace(microsecond=0).time()
    print('+-------END EXECUTION JOB SCHEDULER [%s]-------+\n' % now.isoformat(timespec='microseconds'))

def make_ping_to_payment_gateway(payment_gateway_name):
        try:
            payment_gateway_status_response = requests.get(f"http://{payment_gateway_name}:6000/ping")

            if payment_gateway_status_response.status_code==200 and current_payment_gateway_status[payment_gateway_name] != payment_gateway_status_response.echo:
                notify_payment_gateway_status(payment_gateway_name, payment_gateway_status_response.echo)

            elif payment_gateway_status_response.status_code!=200:
                notify_payment_gateway_status(payment_gateway_name, "down")

        except:
            if current_payment_gateway_status[payment_gateway_name] != "down":
                notify_payment_gateway_status(payment_gateway_name, "down") 
    
def notify_payment_gateway_status(payment_gateway, new_payment_gateway_status):
    current_status_pg = current_payment_gateway_status[payment_gateway]

    try:
        message = {payment_gateway: new_payment_gateway_status}
        current_payment_gateway_status[payment_gateway] = new_payment_gateway_status

        r.publish('payment_gateway_status', str(message))
        print('NOTIFY PAYMENT_GATWAY CHANGE STATE -> {%s:%s}' % (payment_gateway, new_payment_gateway_status))

    except:
        current_payment_gateway_status[payment_gateway] = current_status_pg

def repeat_task():
    scheduler.enter(0, 1, execute_ping_to_payment_gateways, ())
    scheduler.enter(15, 1, repeat_task, ())


class MonitorHealthResource(Resource):
    def get(self):
        return {"status": "up!"}
    
class PaymentGatewayHealthresource(Resource):
    def get(self, payment_gateway_name):
        make_ping_to_payment_gateway(payment_gateway_name) 

api.add_resource(MonitorHealthResource, '/monitor/health-check')
api.add_resource(PaymentGatewayHealthresource, '/monitor/test-ping/<string:payment_gateway_name>')
scheduler = sched.scheduler(time.time, time.sleep)

repeat_task()
scheduler.run()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
