from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.user import User


def seed():
    db = SessionLocal()

    try:
        existing_user = db.scalar(
            select(User).where(User.email == "demo@example.com")
        )

        if existing_user:
            print("Demo user already exists")
            return

        user = User(
            email="demo@example.com",
            password_hash="temporary",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print(f"Created demo user with ID {user.id}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()