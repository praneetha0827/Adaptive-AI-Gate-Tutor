import jwt

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password


def test_password_hash_round_trip() -> None:
    password = "correct horse battery staple"
    assert verify_password(password, hash_password(password))
    assert not verify_password("wrong password", hash_password(password))


def test_access_token_contains_subject() -> None:
    token = create_access_token("user-id")
    claims = jwt.decode(token, get_settings().jwt_secret_key, algorithms=[get_settings().jwt_algorithm])
    assert claims["sub"] == "user-id"

