import os

os.environ["DATABASE_URL"] = "sqlite:///./test_expense.db"
os.environ["SECRET_KEY"] = "testsecretkeyforpytest1234567890"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

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


def get_auth_headers(email: str = "expense_user@example.com", password: str = "testpassword123"):
    # Signup
    client.post(
        "/auth/signup",
        json={"email": email, "password": password},
    )
    # Login
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_expense():
    headers = get_auth_headers()
    response = client.post(
        "/expenses",
        json={
            "title": "Groceries",
            "amount": 120.5,
            "category": "Food",
            "description": "Weekly groceries",
        },
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Groceries"
    assert data["amount"] == 120.5
    assert data["category"] == "Food"
    assert data["description"] == "Weekly groceries"
    assert "id" in data
    assert "date" in data
    assert "user_id" in data


def test_get_all_expenses():
    headers = get_auth_headers()
    client.post(
        "/expenses",
        json={
            "title": "Coffee",
            "amount": 4.5,
            "category": "Food",
        },
        headers=headers,
    )
    response = client.get("/expenses", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_expense_by_id():
    headers = get_auth_headers()
    create_response = client.post(
        "/expenses",
        json={
            "title": "Transport",
            "amount": 45.0,
            "category": "Travel",
        },
        headers=headers,
    )
    expense_id = create_response.json()["id"]

    response = client.get(f"/expenses/{expense_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Transport"


def test_update_expense():
    headers = get_auth_headers()
    create_response = client.post(
        "/expenses",
        json={
            "title": "Movie",
            "amount": 20.0,
            "category": "Entertainment",
        },
        headers=headers,
    )
    expense_id = create_response.json()["id"]

    response = client.put(
        f"/expenses/{expense_id}",
        json={
            "title": "Movie Night",
            "amount": 25.5,
            "category": "Entertainment",
            "description": "Updated ticket",
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Movie Night"
    assert data["amount"] == 25.5
    assert data["description"] == "Updated ticket"


def test_delete_expense():
    headers = get_auth_headers()
    create_response = client.post(
        "/expenses",
        json={
            "title": "Books",
            "amount": 15.0,
            "category": "Learning",
        },
        headers=headers,
    )
    expense_id = create_response.json()["id"]

    response = client.delete(f"/expenses/{expense_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["detail"] == "Expense deleted successfully"

    get_response = client.get(f"/expenses/{expense_id}", headers=headers)
    assert get_response.status_code == 404


def test_total_and_category_summary():
    headers = get_auth_headers()
    client.post(
        "/expenses",
        json={
            "title": "Lunch",
            "amount": 30.0,
            "category": "Food",
        },
        headers=headers,
    )
    client.post(
        "/expenses",
        json={
            "title": "Bus ticket",
            "amount": 20.0,
            "category": "Travel",
        },
        headers=headers,
    )

    total_response = client.get("/expenses/total", headers=headers)
    assert total_response.status_code == 200
    assert total_response.json()["total_expenses"] == 50.0

    category_response = client.get("/expenses/category-summary", headers=headers)
    assert category_response.status_code == 200
    data = category_response.json()
    assert isinstance(data, list)
    assert len(data) == 2
