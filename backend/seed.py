from app.db import Base,engine,SessionLocal
from app.models import User
from app.auth import hash_password
Base.metadata.create_all(bind=engine)
db=SessionLocal()
for name,email in [('Joaco','joaco@twogether.local'),('Selena','selena@twogether.local')]:
    if not db.query(User).filter_by(email=email).first(): db.add(User(name=name,email=email,hashed_password=hash_password('twogether123')))
db.commit(); db.close(); print('Seeded Joaco and Selena')
