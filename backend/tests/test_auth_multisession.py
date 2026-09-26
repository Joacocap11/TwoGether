import os

os.environ['DATABASE_URL'] = 'sqlite:///./test_twogether.db'
os.environ['TESTING'] = 'true'
os.environ['REGISTRATION_ENABLED'] = 'true'

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine, SessionLocal
from app.models import RefreshToken, User
from app.auth import hash_password
from app.config import settings

Base.metadata.create_all(engine)
client = TestClient(app)

# Same rationale as tests/test_auth.py: /auth/register caps total users at 2,
# counting every row regardless of how it was created, so this module seeds
# users directly (bypassing the cap) and wipes them at teardown to hand
# tests/test_ratings.py a clean slate when the whole suite runs together.


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


def login_web(email):
    """Simulate a browser login: refresh token arrives ONLY as an httpOnly
    cookie on the response, never in the JSON body."""
    make_user(email)
    client.cookies.clear()
    r = client.post('/api/v1/auth/login', data={'username': email, 'password': 'password123'})
    assert r.status_code == 200
    refresh_cookie = r.cookies.get(settings.refresh_cookie_name)
    assert refresh_cookie, 'web login must receive the refresh token as a cookie'
    assert r.json().get('refresh_token') is None, 'web login must never expose the refresh token in JSON'
    client.cookies.clear()  # never let it leak into the shared jar between simulated "devices"
    return {'access_token': r.json()['access_token'], 'refresh_token': refresh_cookie}


def login_mobile(email):
    """Simulate a mobile login: refresh token arrives ONLY in the JSON body."""
    make_user(email)
    r = client.post('/api/v1/auth/login', data={'username': email, 'password': 'password123', 'client_id': 'mobile'})
    assert r.status_code == 200
    body = r.json()
    assert body.get('refresh_token'), 'mobile login must receive the refresh token in the JSON body'
    return {'access_token': body['access_token'], 'refresh_token': body['refresh_token']}


def refresh_web(refresh_token):
    client.cookies.clear()
    r = client.post('/api/v1/auth/refresh', cookies={settings.refresh_cookie_name: refresh_token})
    client.cookies.clear()
    return r


def refresh_mobile(refresh_token):
    return client.post('/api/v1/auth/refresh', json={'refresh_token': refresh_token})


def logout_web(refresh_token):
    client.cookies.clear()
    r = client.post('/api/v1/auth/logout', cookies={settings.refresh_cookie_name: refresh_token})
    client.cookies.clear()
    return r


def logout_mobile(refresh_token):
    return client.post('/api/v1/auth/logout', json={'refresh_token': refresh_token})


def me(access_token):
    return client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {access_token}'})


def test_multisession_a_web_and_mobile_logins_are_independent_sessions():
    web = login_web('multisession-a@example.com')
    mobile = login_mobile('multisession-a@example.com')
    assert web['refresh_token'] != mobile['refresh_token']
    assert me(web['access_token']).status_code == 200
    assert me(mobile['access_token']).status_code == 200


def test_multisession_b_refresh_web_does_not_invalidate_mobile():
    web = login_web('multisession-b@example.com')
    mobile = login_mobile('multisession-b@example.com')
    assert refresh_web(web['refresh_token']).status_code == 200
    # Mobile's untouched refresh token must still work afterward.
    assert refresh_mobile(mobile['refresh_token']).status_code == 200


def test_multisession_c_refresh_mobile_does_not_invalidate_web():
    web = login_web('multisession-c@example.com')
    mobile = login_mobile('multisession-c@example.com')
    assert refresh_mobile(mobile['refresh_token']).status_code == 200
    # Web's untouched refresh token must still work afterward.
    assert refresh_web(web['refresh_token']).status_code == 200


def test_multisession_d_logout_web_does_not_invalidate_mobile():
    web = login_web('multisession-d@example.com')
    mobile = login_mobile('multisession-d@example.com')
    assert logout_web(web['refresh_token']).status_code == 204
    # Mobile's independent session must remain valid after a WEB-ONLY
    # logout, with no further use of the now-dead web token (see test H
    # for what happens if the dead web token is then refreshed).
    assert refresh_mobile(mobile['refresh_token']).status_code == 200


def test_multisession_e_logout_mobile_does_not_invalidate_web():
    web = login_web('multisession-e@example.com')
    mobile = login_mobile('multisession-e@example.com')
    assert logout_mobile(mobile['refresh_token']).status_code == 204
    # Web's independent session must remain valid after a MOBILE-ONLY
    # logout, with no further use of the now-dead mobile token.
    assert refresh_web(web['refresh_token']).status_code == 200


def test_multisession_f_one_users_sessions_never_affect_another_users():
    user_a = login_mobile('multisession-f-a@example.com')
    user_b = login_mobile('multisession-f-b@example.com')
    # Refresh tokens are single-use/rotating: capture the NEW token from
    # each response rather than reusing an already-consumed one.
    a_refreshed = refresh_mobile(user_a['refresh_token'])
    assert a_refreshed.status_code == 200
    a_token_2 = a_refreshed.json()['refresh_token']
    b_refreshed_1 = refresh_mobile(user_b['refresh_token'])
    assert b_refreshed_1.status_code == 200  # untouched by A's activity
    b_token_2 = b_refreshed_1.json()['refresh_token']
    assert logout_mobile(a_token_2).status_code == 204
    b_refreshed_2 = refresh_mobile(b_token_2)
    assert b_refreshed_2.status_code == 200  # still untouched by A's refresh + logout


def test_multisession_g_reuse_of_rotated_web_token_scopes_to_web_family_only():
    """
    Reusing a refresh token that was already rotated away (revoked_reason
    == 'rotation') is treated as potential theft, but the fix scopes the
    cascade to that token's own family_id only -- an unrelated session for
    the SAME user (mobile) must stay valid, and a different user entirely
    must never be touched.
    """
    email = 'multisession-g@example.com'
    web = login_web(email)
    stolen = web['refresh_token']
    rotated = refresh_web(stolen)
    assert rotated.status_code == 200

    mobile = login_mobile(email)  # unrelated family, same user
    other_user = login_mobile('multisession-g-other@example.com')

    # Replay the already-rotated (stale) web token -> reuse detected -> 401,
    # and only the web family gets killed as a side effect.
    assert refresh_web(stolen).status_code == 401

    # Mobile's independent family for the SAME user survives.
    assert refresh_mobile(mobile['refresh_token']).status_code == 200
    # A different user is untouched.
    assert refresh_mobile(other_user['refresh_token']).status_code == 200


def test_multisession_h_reuse_of_logged_out_token_does_not_cascade():
    """
    A refresh token revoked via a normal /auth/logout (revoked_reason ==
    'logout') is NOT treated as theft. Reusing it (e.g. a stale background
    timer racing a manual logout) must simply fail 401, with zero side
    effects on any other session -- unlike rotation-reuse, this must not
    even touch its own family, let alone anyone else's.
    """
    web = login_web('multisession-h@example.com')
    mobile = login_mobile('multisession-h@example.com')
    assert logout_web(web['refresh_token']).status_code == 204
    # Re-attempting a refresh with the now-logged-out web token just 401s.
    assert refresh_web(web['refresh_token']).status_code == 401
    # Mobile's completely unrelated session is untouched.
    assert refresh_mobile(mobile['refresh_token']).status_code == 200


def test_multisession_i_two_mobile_logins_same_user_get_independent_families():
    email = 'multisession-i@example.com'
    session1 = login_mobile(email)
    session2 = login_mobile(email)
    with SessionLocal() as db:
        import hashlib
        h1 = hashlib.sha256(session1['refresh_token'].encode()).hexdigest()
        h2 = hashlib.sha256(session2['refresh_token'].encode()).hexdigest()
        row1 = db.query(RefreshToken).filter_by(token_hash=h1).first()
        row2 = db.query(RefreshToken).filter_by(token_hash=h2).first()
        assert row1.family_id != row2.family_id
    assert refresh_mobile(session1['refresh_token']).status_code == 200
    assert refresh_mobile(session2['refresh_token']).status_code == 200


def test_multisession_j_reuse_in_mobile_session_1_does_not_affect_mobile_session_2():
    email = 'multisession-j@example.com'
    session1 = login_mobile(email)
    session2 = login_mobile(email)
    stolen = session1['refresh_token']
    assert refresh_mobile(stolen).status_code == 200  # rotate session1 once
    assert refresh_mobile(stolen).status_code == 401   # reuse -> kills session1's family only
    assert refresh_mobile(session2['refresh_token']).status_code == 200  # untouched


def test_multisession_k_family_id_persists_across_multiple_rotations():
    email = 'multisession-k@example.com'
    session = login_mobile(email)
    with SessionLocal() as db:
        import hashlib
        h0 = hashlib.sha256(session['refresh_token'].encode()).hexdigest()
        original_family = db.query(RefreshToken).filter_by(token_hash=h0).first().family_id
    token = session['refresh_token']
    for _ in range(3):
        r = refresh_mobile(token)
        assert r.status_code == 200
        token = r.json()['refresh_token']
        with SessionLocal() as db:
            import hashlib
            h = hashlib.sha256(token.encode()).hexdigest()
            row = db.query(RefreshToken).filter_by(token_hash=h).first()
            assert row.family_id == original_family


def test_multisession_l_reuse_of_an_already_reuse_revoked_token_has_no_new_side_effects():
    email = 'multisession-l@example.com'
    stolen_family = login_mobile(email)
    other_family = login_mobile(email)  # second, independent session for the same user
    other_user = login_mobile('multisession-l-other@example.com')

    rotated = refresh_mobile(stolen_family['refresh_token'])
    assert rotated.status_code == 200
    # First reuse: detected, kills stolen_family's family only.
    assert refresh_mobile(stolen_family['refresh_token']).status_code == 401
    # Sanity: the other same-user family and the other user are still fine
    # right after the first reuse was handled.
    assert refresh_mobile(other_family['refresh_token']).status_code == 200
    assert refresh_mobile(other_user['refresh_token']).status_code == 200

    # Second reuse attempt of the SAME already-reuse-revoked token: still
    # just fails, no additional/new side effects anywhere.
    assert refresh_mobile(stolen_family['refresh_token']).status_code == 401
    assert refresh_mobile(rotated.json()['refresh_token']).status_code == 401  # its child, same dead family
