
from faker import Faker
from api import db
from models import *

db.create_all()

faker = Faker()

for i in range(10):
    user_name = faker.unique.name()
    user = User(id=i, full_name=user_name, email=f"{user_name}@{faker.random.domain_name()}", plan=faker.random.choice([PlanType.BASIC.value, PlanType.PREMIUM.value]))
    
    db.session.add(user)
    db.session.commit()