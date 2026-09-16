from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User


class EmailAlreadyRegisteredError(Exception):
    pass


def register_user(database: Session, email: str, password: str) -> User:
    normalized_email = email.lower()
    if database.scalar(select(User).where(User.email == normalized_email)):
        raise EmailAlreadyRegisteredError
    user = User(email=normalized_email, password_hash=hash_password(password))
    database.add(user)
    database.commit()
    database.refresh(user)
    return user


def authenticate_user(database: Session, email: str, password: str) -> User | None:
    user = database.scalar(select(User).where(User.email == email.lower()))
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user

