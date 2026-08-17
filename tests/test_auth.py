import os
from datetime import timedelta

os.environ["DATABASE_URL"] = "sqlite:///./test_expense.db"
os.environ["SECRET_KEY"] = "testsecretkeyforpytest1234567890"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from auth import create_access_token
from database import Base, get_db
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_expense.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_user_signup_success():
    response = client.post(
        "/auth/signup",
        json={"email": "alice@example.com", "password": "securepassword123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert "id" in data
    # Ensure password and hashed_password are NEVER exposed in response
    assert "password" not in data
    assert "hashed_password" not in data


def test_user_duplicate_signup_fails():
    client.post(
        "/auth/signup",
        json={"email": "alice@example.com", "password": "securepassword123"},
    )
    response = client.post(
        "/auth/signup",
        json={"email": "alice@example.com", "password": "anotherpassword"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_user_login_success():
    client.post(
        "/auth/signup",
        json={"email": "bob@example.com", "password": "mypassword123"},
    )
    response = client.post(
        "/auth/login",
        data={"username": "bob@example.com", "password": "mypassword123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_user_login_incorrect_password():
    client.post(
        "/auth/signup",
        json={"email": "bob@example.com", "password": "mypassword123"},
    )
    response = client.post(
        "/auth/login",
        data={"username": "bob@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_user_login_nonexistent_user():
    response = client.post(
        "/auth/login",
        data={"username": "nobody@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_unauthorized_access_without_token():
    response = client.get("/expenses")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_unauthorized_access_with_invalid_token():
    response = client.get(
        "/expenses",
        headers={"Authorization": "Bearer invalid.token.payload"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_unauthorized_access_with_expired_token():
    # Generate an expired token
    expired_token = create_access_token(
        data={"sub": "alice@example.com"},
        expires_delta=timedelta(minutes=-10),
    )
    response = client.get(
        "/expenses",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_user_data_isolation():
    # Register Alice and Bob
    client.post(
        "/auth/signup",
        json={"email": "alice@example.com", "password": "password123"},
    )
    alice_login = client.post(
        "/auth/login",
        data={"username": "alice@example.com", "password": "password123"},
    )
    alice_token = alice_login.json()["access_token"]
    alice_headers = {"Authorization": f"Bearer {alice_token}"}

    client.post(
        "/auth/signup",
        json={"email": "bob@example.com", "password": "password123"},
    )
    bob_login = client.post(
        "/auth/login",
        data={"username": "bob@example.com", "password": "password123"},
    )
    bob_token = bob_login.json()["access_token"]
    bob_headers = {"Authorization": f"Bearer {bob_token}"}

    # Alice creates an expense
    alice_exp = client.post(
        "/expenses",
        json={"title": "Alice Gym", "amount": 50.0, "category": "Health"},
        headers=alice_headers,
    ).json()

    # Bob creates an expense
    bob_exp = client.post(
        "/expenses",
        json={"title": "Bob Dinner", "amount": 30.0, "category": "Food"},
        headers=bob_headers,
    ).json()

    # 1. Bob cannot see Alice's expense in list
    bob_list = client.get("/expenses", headers=bob_headers).json()
    assert len(bob_list) == 1
    assert bob_list[0]["title"] == "Bob Dinner"

    # 2. Bob cannot get Alice's expense by ID (404)
    bob_get_alice = client.get(f"/expenses/{alice_exp['id']}", headers=bob_headers)
    assert bob_get_alice.status_code == 404

    # 3. Bob cannot update Alice's expense (404)
    bob_update_alice = client.put(
        f"/expenses/{alice_exp['id']}",
        json={"title": "Hacked", "amount": 100.0, "category": "Health"},
        headers=bob_headers,
    )
    assert bob_update_alice.status_code == 404

    # 4. Bob cannot delete Alice's expense (404)
    bob_del_alice = client.delete(f"/expenses/{alice_exp['id']}", headers=bob_headers)
    assert bob_del_alice.status_code == 404

    # 5. Alice's expense still exists intact
    alice_get_own = client.get(f"/expenses/{alice_exp['id']}", headers=alice_headers)
    assert alice_get_own.status_code == 200
    assert alice_get_own.json()["title"] == "Alice Gym"

    # 6. Total expenses are user-specific
    alice_total = client.get("/expenses/total", headers=alice_headers).json()
    bob_total = client.get("/expenses/total", headers=bob_headers).json()
    assert alice_total["total_expenses"] == 50.0
    assert bob_total["total_expenses"] == 30.0

    # 7. Category summary is user-specific
    alice_cat = client.get("/expenses/category-summary", headers=alice_headers).json()
    bob_cat = client.get("/expenses/category-summary", headers=bob_headers).json()
    assert alice_cat == [{"category": "Health", "total_amount": 50.0}]
    assert bob_cat == [{"category": "Food", "total_amount": 30.0}]
