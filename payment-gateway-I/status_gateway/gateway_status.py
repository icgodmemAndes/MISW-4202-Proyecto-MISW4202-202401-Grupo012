import random
import threading
import time
from gateway_events.trace_event import TraceEvent
from models import db, ServiceStatus

#define two constants to simulate the gateway status
GATEWAY_DOWN = "down"
GATEWAY_UP = "up"

class GatewayStatus:
    
    tracer = TraceEvent(db)

    def __init__(self, db) -> None:
        #initialize the gateway status
        self.db = db
        self.timer = None
        self.set_gateway_status(GATEWAY_UP)


    def execute_ping(self, echo):
        #if the gateway is down return a 400 http status code, 
        #if not return a 200 http status code and the echo message
        rand = random.random()
        alive = self.is_gateway_alive()

        print('[Execute Ping] {}, {}'.format(alive, rand))

        if not alive or rand > 0.8:
            #trace event
            self.tracer.save("Ping: Gateway is down", echo)
            return "Service is unavailable", 503
        else:
            #trace event
            self.tracer.save("Ping: Gateway is up", echo)
            return echo, 200
    
    def simulate_gateway_down(self):
        #Initialize a new timer with a random time from 10 to 25 seconds,
        #when the timer ends the gateway is up again
        until = random.randint(1, 2)
       
        #trace event
        self.set_gateway_status(GATEWAY_DOWN)
        self.tracer.save("Timer: simulated down", str(until) + " seconds")       
        time.sleep(until)
        self.set_gateway_up()
        
    def set_gateway_up(self):
        #trace event
        self.tracer.save("Timer Elasped", "gateway is up again")
        self.set_gateway_status(GATEWAY_UP)
    
    def set_gateway_status(self, _status):
        #delete all statuses and add a new one
        #delete all

        self.db.session.query(ServiceStatus).delete()
        self.db.session.add(ServiceStatus(status=_status))
        self.db.session.commit()
    
    def is_gateway_alive(self): 
        #return the current status of the gateway
        #get the first record from GatewayStatus from db

        status = self.db.session.query(ServiceStatus.status).one_or_none()
      
        if status is not None:
            if status[0] == GATEWAY_DOWN:
                return False
            else:
                return True
        
        return False
