#Save a new event to the db
import datetime

class TraceEvent:

    def __init__(self, db):
        self.db = db

    def save(self, name, value):
        from models import Event
        event = Event(name=name, date=datetime.datetime.now(), value=value)
        self.db.session.add(event)
        self.db.session.commit()
        return event.id