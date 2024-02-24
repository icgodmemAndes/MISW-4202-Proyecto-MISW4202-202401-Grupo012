from flask import request
from flask_restful import Resource
from status_gateway.gateway_status import GatewayStatus
from models import db


class ViewPing(Resource):

    def __init__(self):
        self.status = GatewayStatus(db)

    def get(self):      
        try:
            #get content from query string
            echo = request.args.get('echo')
            return self.status.execute_ping(echo)
        except:
            return "Bad request", 400

            
            
                   
        
    
    
