#import GatewayStatus to simulate the gateway status
from status_gateway.gateway_status import GatewayStatus
from gateway_events.trace_event import TraceEvent

#Simulate a payment, recieve a payment model and execute a random calculation from 0 to 1 to simulate the payment, if the random number is close to 1 return a 200 http status code, if not return a 400 http status code
class PaymentProcessor: 
    
    def __init__(self, db):
        self.status = GatewayStatus(db)
        self.tracer = TraceEvent(db)

    def process_payment(self, db , payment):
        import random

        if not self.status.is_gateway_alive():
            #return http service unavailable status code
            return "Gateway is down", 503

        if random.random() <= 0.8:
            db.session.add(payment)
            db.session.commit()

            #Save a new event to the db
            self.tracer.save("Payment Executed Succesfully", payment.id)

            return "Payment Executed Successfully", 200
        else:
            self.tracer.save("Payment Failed", payment.id)
            self.status.simulate_gateway_down()
            return  "Payment Failed", 400
    
    def retry_payment(self, db, payment):
        if not self.status.is_gateway_alive():
            #return http service unavailable status code
            return "Gateway is down", 503
        
        db.session.add(payment)
        db.session.commit()

        #trace event
        self.tracer.save("Payment Retried", payment.id)
        return "Retry Payment Executed Successfully", 200
    

