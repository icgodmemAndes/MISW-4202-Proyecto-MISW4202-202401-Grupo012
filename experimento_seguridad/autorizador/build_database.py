cd ..
from faker import Faker
from api import db
from models import *

db.create_all()

faker = Faker()

for i in range(10):
    user_name = faker.unique.name()
    user = User(id=i, username=user_name, password=f"user_security_experiment_{i}",  user_id=i, roles=faker.random.choice(["full_access", "basic_user", "premium_user"]), is_blocked=False)
    
    db.session.add(user)
    db.session.commit()