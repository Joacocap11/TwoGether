import hashlib
import os
import pytest
from datetime import datetime, timedelta, timezone

os.environ['DATABASE_URL'] = 'sqlite:///./test_twogether.db'
os.environ['TESTING'] = 'true'
os.environ['REGISTRATION_ENABLED'] = 'true'

from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine, SessionLocal
from app.models import RefreshToken, User
from app.auth import hash_password
from app.config import settings

Base.metadata.create_all(engine)
client = TestClient(app)

# The app enforces a hard cap of 2 registered users via POST /auth/register
# (private couple's app). Auth/refresh scenarios need many disposable users,
# so tests seed them directly in the DB (same pattern as backend/seed.py),
# bypassing the registration cap entirely instead of fighting over it with
# tests/test_ratings.py when the whole suite runs together via bare `pytest`.
#
# Cleanup: /auth/register's cap counts ALL rows regardless of how they were
# created, so once this module is done, wipe every seeded user/refresh_token
# back to zero — otherwise test_ratings.py (which registers its own 2 users)
# would find the cap already exhausted when the whole suite runs together.
@pytest.fixture(scope='module', autouse=True)
def _cleanup_seeded_users():
    yield
    with SessionLocal() as db:
        db.query(RefreshToken).delete()
        db.query(User).delete()
        db.commit()

def make_user(email):
    with SessionLocal() as db:
        existing = db.query(User).filter_by(email=email).first()
        if existing:
            return existing.id
        user = User(name=email, email=email, hashed_password=hash_password('password123'))
        db.add(user); db.commit(); db.refresh(user)
        return user.id


def login(email, client_id=None):
    make_user(email)
    data = {'username': email, 'password': 'password123'}
    if client_id:
        data['client_id'] = client_id
    r = client.post('/api/v1/auth/login', data=data)
    assert r.status_code == 200
    return r


def test_a_login_returns_access_and_web_gets_cookie_not_body_token():
    r = login('web-user@example.com')
    body = r.json()
    assert 'access_token' in body and body['access_token']
    # Web client: refresh token must NOT be exposed in the JSON body.
    assert body.get('refresh_token') is None
    assert settings.refresh_cookie_name in r.cookies


def test_a2_mobile_login_receives_refresh_token_in_body_no_cookie_required():
    r = login('mobile-user@example.com', client_id='mobile')
    body = r.json()
    assert body.get('refresh_token')


def test_b_me_accepts_valid_access_token():
    r = login('me-user@example.com')
    token = r.json()['access_token']
    me = client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert me.status_code == 200 and me.json()['email'] == 'me-user@example.com'


def test_c_expired_access_token_returns_401():
    from jose import jwt
    make_user('expired-access@example.com')
    expired = jwt.encode(
        {'sub': '1', 'exp': datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.secret_key, algorithm='HS256',
    )
    r = client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {expired}'})
    assert r.status_code == 401


def test_d_e_f_refresh_rotates_and_old_token_cannot_be_reused():
    r = login('rotate-user@example.com', client_id='mobile')
    old_refresh = r.json()['refresh_token']

    # D: valid refresh returns a new access token.
    refreshed = client.post('/api/v1/auth/refresh', json={'refresh_token': old_refresh})
    assert refreshed.status_code == 200
    new_access = refreshed.json()['access_token']
    new_refresh = refreshed.json()['refresh_token']
    assert new_access and new_refresh

    # E: rotation issued a different refresh token than the one used.
    assert new_refresh != old_refresh

    # F: the old (now revoked) refresh token cannot be reused.
    reuse = client.post('/api/v1/auth/refresh', json={'refresh_token': old_refresh})
    assert reuse.status_code == 401

    # Reuse-detection side effect: the new token issued by rotation shares
    # the same family_id as the reused token, so it is revoked too (still
    # just this one lineage/family, not every session of the user).
    new_token_after_reuse = client.post('/api/v1/auth/refresh', json={'refresh_token': new_refresh})
    assert new_token_after_reuse.status_code == 401


def test_g_expired_refresh_token_fails():
    r = login('expired-refresh@example.com', client_id='mobile')
    raw_refresh = r.json()['refresh_token']
    with SessionLocal() as db:
        token_hash = hashlib.sha256(raw_refresh.encode()).hexdigest()
        row = db.query(RefreshToken).filter_by(token_hash=token_hash).first()
        row.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)
        db.commit()
    r2 = client.post('/api/v1/auth/refresh', json={'refresh_token': raw_refresh})
    assert r2.status_code == 401


def test_h_revoked_refresh_token_fails():
    r = login('revoked-refresh@example.com', client_id='mobile')
    raw_refresh = r.json()['refresh_token']
    with SessionLocal() as db:
        token_hash = hashlib.sha256(raw_refresh.encode()).hexdigest()
        row = db.query(RefreshToken).filter_by(token_hash=token_hash).first()
        row.revoked_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.commit()
    r2 = client.post('/api/v1/auth/refresh', json={'refresh_token': raw_refresh})
    assert r2.status_code == 401


def test_i_logout_revokes_refresh_token():
    r = login('logout-user@example.com', client_id='mobile')
    raw_refresh = r.json()['refresh_token']
    logout = client.post('/api/v1/auth/logout', json={'refresh_token': raw_refresh})
    assert logout.status_code == 204
    r2 = client.post('/api/v1/auth/refresh', json={'refresh_token': raw_refresh})
    assert r2.status_code == 401


def test_i2_web_logout_clears_cookie_and_revokes_it():
    r = login('web-logout@example.com')
    cookie_value = r.cookies.get(settings.refresh_cookie_name)
    assert cookie_value
    client.cookies.set(settings.refresh_cookie_name, cookie_value)
    logout = client.post('/api/v1/auth/logout')
    assert logout.status_code == 204
    # Cookie-based refresh must be revoked too.
    refresh_attempt = client.post('/api/v1/auth/refresh', json={'refresh_token': cookie_value})
    assert refresh_attempt.status_code == 401
    client.cookies.clear()


def test_j_nonexistent_or_inactive_user_cannot_refresh():
    r = login('deactivate-user@example.com', client_id='mobile')
    raw_refresh = r.json()['refresh_token']
    with SessionLocal() as db:
        db.query(User).filter(User.email == 'deactivate-user@example.com').update({'is_active': False})
        db.commit()
    r2 = client.post('/api/v1/auth/refresh', json={'refresh_token': raw_refresh})
    assert r2.status_code == 401


def test_k_refresh_token_not_stored_plaintext_in_db():
    r = login('plaintext-check@example.com', client_id='mobile')
    raw_refresh = r.json()['refresh_token']
    with SessionLocal() as db:
        rows = db.query(RefreshToken).all()
        for row in rows:
            assert row.token_hash != raw_refresh
            assert len(row.token_hash) == 64  # sha256 hex digest length


def test_missing_refresh_token_returns_401():
    r = client.post('/api/v1/auth/refresh', json={})
    assert r.status_code == 401
