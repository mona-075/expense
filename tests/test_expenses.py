import os

os.environ["DATABASE_URL"] = "sqlite:///./test_expense.db"

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


def test_create_expense():
    response = client.post(
        "/expenses",
        json={
            "title": "Groceries",
            "amount": 120.5,
            "category": "Food",
            "description": "Weekly groceries",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Groceries"
    assert data["amount"] == 120.5
    assert data["category"] == "Food"
    assert data["description"] == "Weekly groceries"
    assert "id" in data
    assert "date" in data


def test_get_all_expenses():
    response = client.get("/expenses")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_expense_by_id():
    create_response = client.post(
        "/expenses",
        json={
            "title": "Transport",
            "amount": 45.0,
            "category": "Travel",
        },
    )
    expense_id = create_response.json()["id"]

    response = client.get(f"/expenses/{expense_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Transport"


def test_update_expense():
    create_response = client.post(
        "/expenses",
        json={
            "title": "Movie",
            "amount": 20.0,
            "category": "Entertainment",
        },
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
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Movie Night"
    assert data["amount"] == 25.5
    assert data["description"] == "Updated ticket"


def test_delete_expense():
    create_response = client.post(
        "/expenses",
        json={
            "title": "Books",
            "amount": 15.0,
            "category": "Learning",
        },
    )
    expense_id = create_response.json()["id"]

    response = client.delete(f"/expenses/{expense_id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Expense deleted successfully"

    get_response = client.get(f"/expenses/{expense_id}")
    assert get_response.status_code == 404


def test_total_and_category_summary():
    client.post(
        "/expenses",
        json={
            "title": "Lunch",
            "amount": 30.0,
            "category": "Food",
        },
    )
    client.post(
        "/expenses",
        json={
            "title": "Bus ticket",
            "amount": 20.0,
            "category": "Travel",
        },
    )

    total_response = client.get("/expenses/total")
    assert total_response.status_code == 200
    assert total_response.json()["total_expenses"] >= 50.0

    category_response = client.get("/expenses/category-summary")
    assert category_response.status_code == 200
    data = category_response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
