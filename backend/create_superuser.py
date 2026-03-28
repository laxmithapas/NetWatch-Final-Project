import os
import sys

# Add backend to path so imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.alert import Alert
from app.core.security import get_password_hash

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    user = db.query(User).filter(User.email == "admin@netwatch.local").first()
    if not user:
        user = User(
            email="admin@netwatch.local",
            hashed_password=get_password_hash("admin123"),
            full_name="System Admin",
            is_superuser=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print("Superuser created successfully: admin@netwatch.local / admin123")
    else:
        print("Superuser already exists.")
    
    db.close()

if __name__ == "__main__":
    init_db()
