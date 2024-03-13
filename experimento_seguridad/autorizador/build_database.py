from faker import Faker
from app import db
from models import User

db.drop_all()
db.create_all()

faker = Faker()

for i in range(10):
    user_name = faker.unique.word()
    user = User(id=i, username=user_name, password=f"use_{i}", user_id=i,
                roles=faker.random.choice(["full_access", "basic_user", "premium_user", "guest"]), is_blocked=False)

    db.session.add(user)
    db.session.commit()
