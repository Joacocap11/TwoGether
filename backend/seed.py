import os
from app.db import SessionLocal
from app.models import User
from app.auth import hash_password

joaco_password = os.environ.get('INITIAL_JOACO_PASSWORD')
selena_password = os.environ.get('INITIAL_SELENA_PASSWORD')
if not joaco_password or not selena_password:
    raise SystemExit('Set INITIAL_JOACO_PASSWORD and INITIAL_SELENA_PASSWORD in the private environment')

db = SessionLocal()
try:
    for name, email, password in [
        ('Joaco', 'joaco@twogether.local', joaco_password),
        ('Selena', 'selena@twogether.local', selena_password),
    ]:
        user = db.query(User).filter_by(email=email).first()
        if not user:
            db.add(User(name=name, email=email, hashed_password=hash_password(password)))
    db.commit()
finally:
    db.close()
print('Seeded Joaco and Selena')
