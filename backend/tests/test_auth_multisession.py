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


def test_multisession_h_refreshing_an_already_logged_out_token_revokes_other_sessions_too():
    """
    A more severe variant of the same reuse-detection design issue as test G,
    triggered by a perfectly ordinary sequence with NO attacker involved:

    1. User logs out on device 1 (web) -> device 1's refresh token is
       revoked via /auth/logout.
    2. Something on device 1 (a stale background timer, a double-tap, a
       race between "logout" and a scheduled silent refresh) still fires
       one more /auth/refresh call using that now-revoked token.

    rotate_refresh_token() cannot distinguish "revoked because it was
    rotated away" from "revoked because the user logged out": both just
    have revoked_at set, so step 2 is treated as reuse/theft and revokes
    EVERY active session for the user -- silently logging out device 2
    (mobile) as collateral damage, even though device 2 never did
    anything wrong and nobody stole anything.
    """
    web = login_web('multisession-h@example.com')
    mobile = login_mobile('multisession-h@example.com')
    assert logout_web(web['refresh_token']).status_code == 204
    # Re-attempting a refresh with the now-logged-out web token is treated
    # as reuse of a revoked token -> 401, AND cascades:
    assert refresh_web(web['refresh_token']).status_code == 401
    # Mobile's completely unrelated, never-misused session is now dead too.
    assert refresh_mobile(mobile['refresh_token']).status_code == 401




def test_multisession_g_reuse_revocation_scope_is_whole_user_not_just_the_stolen_lineage():
    """
    Documents the CURRENT (as-implemented) scope of the reuse-detection
    safeguard in rotate_refresh_token(): reusing an already-rotated refresh
    token revokes EVERY active refresh token for that user_id — including
    completely unrelated sessions/devices/logins, not just the descendants
    of the stolen token's own lineage. This is broader than "just the
    compromised session" and is flagged for a product decision, not changed
    here.
    """
    email = 'multisession-g@example.com'
    # Session 1 (e.g. phone A): login, then rotate once so the original
    # token becomes "already revoked" (the stolen/stale token an attacker
    # might replay).
    session1 = login_mobile(email)
    stolen = session1['refresh_token']
    rotated = refresh_mobile(stolen)
    assert rotated.status_code == 200
    current_child = rotated.json()['refresh_token']  # direct descendant of `stolen`

    # Session 2 (e.g. phone B, or the web browser): a totally separate
    # login for the SAME user, unrelated lineage to `stolen`.
    session2 = login_mobile(email)

    # A different user must never be touched by any of this.
    other_user = login_mobile('multisession-g-other@example.com')

    # Replay the already-rotated (stale) token -> reuse detected -> 401.
    reuse_attempt = refresh_mobile(stolen)
    assert reuse_attempt.status_code == 401

    # Its direct child (the "legitimate" continuation of that same lineage)
    # is also dead, which is expected regardless of scoping policy.
    assert refresh_mobile(current_child).status_code == 401

    # As currently implemented, session2 -- a fully independent login for
    # the SAME user, sharing no lineage with the stolen token -- is ALSO
    # revoked. This confirms "family" == "every active session belonging to
    # this user_id", not "the lineage descending from the compromised token".
    assert refresh_mobile(session2['refresh_token']).status_code == 401

    # The other user's session is untouched: isolation across users holds
    # even though isolation across a single user's own devices does not.
    assert refresh_mobile(other_user['refresh_token']).status_code == 200
