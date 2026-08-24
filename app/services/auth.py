from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user import UserRepository


class AuthService:
    def __init__(self):
        self.users = UserRepository()

    def register(
        self,
        db: Session,
        email: str,
        password: str,
    ) -> User:
        email = email.strip().lower()

        if self.users.get_by_email(db, email):
            raise ValueError("Email already registered")

        if len(password) < 8:
            raise ValueError(
                "Password must contain at least 8 characters"
            )

        return self.users.create(
            db=db,
            email=email,
            password_hash=hash_password(password),
        )

    def login(
        self,
        db: Session,
        email: str,
        password: str,
    ) -> str:
        user = self.users.get_by_email(
            db,
            email.strip().lower(),
        )

        if user is None:
            raise ValueError("Invalid email or password")

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError("Invalid email or password")

        return create_access_token(user.id)