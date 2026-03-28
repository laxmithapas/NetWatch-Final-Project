import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine
from app.core.security import get_password_hash
from app.models.user import User
from app.core.database import SessionLocal

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Create test user
    user = db.query(User).filter(User.email == "test@netwatch.local").first()
    if not user:
        user = User(
            email="test@netwatch.local",
            hashed_password=get_password_hash("testpass"),
            full_name="Test User",
            is_superuser=False,
        )
        db.add(user)
        db.commit()
    yield
    db.close()

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to NetWatch API"}

def test_login_success(setup_db):
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "test@netwatch.local", "password": "testpass"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure(setup_db):
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "test@netwatch.local", "password": "wrongpassword"},
    )
    assert response.status_code == 400
