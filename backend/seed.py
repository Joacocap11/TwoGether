import os
from app.db import SessionLocal
from app.models import User
from app.auth import hash_password

users = [
    ('Joaco', os.environ.get('INITIAL_JOACO_EMAIL'), os.environ.get('INITIAL_JOACO_PASSWORD')),
    ('Selena', os.environ.get('INITIAL_SELENA_EMAIL'), os.environ.get('INITIAL_SELENA_PASSWORD')),
]
missing = [f'INITIAL_{name.upper()}_EMAIL/PASSWORD' for name, email, password in users if not email or not password]
if missing:
    raise SystemExit('Missing private seed variables: ' + ', '.join(missing))

db = SessionLocal()
created = []
existing = []
try:
    for name, email, password in users:
        user = db.query(User).filter_by(email=email).first()
        if user:
            existing.append(email)
        else:
            db.add(User(name=name, email=email, hashed_password=hash_password(password)))
            created.append(email)
    db.commit()
finally:
    db.close()
print(f'Created: {", ".join(created) if created else "none"}')
print(f'Already existed: {", ".join(existing) if existing else "none"}')
