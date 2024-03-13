


import datetime


class AttempsHandler:

    def __init__(self, db):
        self.db = db
    
    def register_invalid_attemp(self, username):
        from models import Attemps

        attemp = self.db.InvalidAttemps.query.filter_by(username=username).first()

        if attemp is not None:
            attemp.failed_attemps += 1
            attemp.date = datetime.datetime.now()
            self.db.session.add(attemp)
        else:
            attemp = Attemps(username=username, date=datetime.datetime.now(), failed_attemps=1)
            self.db.session.add(attemp)
    
        self.db.session.commit()
        return attemp.id
    
    def reset_attemps(self, username):
        attemp = self.db.InvalidAttemps.query.filter_by(username=username).first()
        if attemp is not None:
            attemp.failed_attemps = 0
            self.db.session.add(attemp)
            self.db.session.commit()
            return attemp.id
        else:
            return None

    def get_attemps(self, username):
        attemp = self.db.InvalidAttemps.query.filter_by(username=username).first()
        if attemp is not None:
            return attemp.failed_attemps
        else:
            return 0    