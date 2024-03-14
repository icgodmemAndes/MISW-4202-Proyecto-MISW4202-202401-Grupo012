from faker import Faker
from app import db
from models import User

db.drop_all()
db.create_all()

faker = Faker()

for i in range(20):
    user = User(id=i, username='user_{}'.format(i), password=f"pass_{i}", user_id=i,
                roles=faker.random.choice(["full_access", "basic_user", "premium_user", "guest"]), is_blocked=False)

    db.session.add(user)
    db.session.commit()
