from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing():
    password = "password123"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_access_token_round_trip():
    token = create_access_token(42)

    user_id = decode_access_token(token)

    assert user_id == 42


def test_invalid_token():
    user_id = decode_access_token(
        "this-is-not-a-valid-jwt"
    )

    assert user_id is None