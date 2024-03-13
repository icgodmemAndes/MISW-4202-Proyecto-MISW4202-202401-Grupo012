from faker import Faker
from models import User, PlanType
from api import db

db.drop_all()
db.create_all()

faker = Faker()

for i in range(10):
    user_name = faker.unique.word()
    user = User(id=i, full_name=user_name, email=f"{user_name}@{faker.word()}.com",
                plan=faker.random.choice([PlanType.BASIC.value, PlanType.PREMIUM.value]))

    db.session.add(user)
    db.session.commit()
