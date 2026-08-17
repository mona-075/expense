# Expense Management API

A secure FastAPI project for tracking personal expenses with JWT authentication and user data isolation.

## Features

- **User Authentication**: Secure sign up and login with bcrypt password hashing and signed JWT tokens.
- **Data Isolation**: Each user can only access, modify, and delete their own expenses.
- **Expense CRUD**: Create, read, update, and delete expenses.
- **Aggregations**: Calculate user-specific total expenses and category-wise spending summaries.
- **Interactive Swagger UI**: Test all endpoints and authenticate via the Authorize button at `/docs`.
- **Database Flexibility**: PostgreSQL support via SQLAlchemy with SQLite fallback.
- **Configurable**: Environment-based configuration via `.env` (kept secure and ignored by Git).

## Tech Stack

- Python 3.13+
- FastAPI
- SQLAlchemy
- PostgreSQL / SQLite
- Pydantic
- bcrypt (Password Hashing)
- PyJWT (JSON Web Tokens)
- Uvicorn
- Pytest

## Project Structure

```text
expense_management/
├── auth.py             # Password hashing, JWT creation & get_current_user dependency
├── crud.py             # User and user-scoped Expense database operations
├── database.py         # SQLAlchemy engine, session maker, and get_db dependency
├── main.py             # FastAPI app, routing, and endpoint protection
├── models.py           # SQLAlchemy User and Expense database models
├── schemas.py          # Pydantic schemas for requests and responses
├── requirements.txt    # Project dependencies
├── .env.example        # Environment variables template
├── .env                # Local secrets and configuration (git-ignored)
├── .gitignore          # Git ignore rules
├── README.md           # Documentation
└── tests/
    ├── test_auth.py    # Authentication, JWT, and user isolation tests
    └── test_expenses.py # Protected expense CRUD and summary tests
```

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file from `.env.example`:

```bash
copy .env.example .env
```

Ensure your `.env` contains:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/expense_db
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

4. Run the API:

```bash
uvicorn main:app --reload
```

5. Open Swagger docs:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Authentication
- `POST /auth/signup` - Register a new user (`email` and `password`).
- `POST /auth/login` - Authenticate with OAuth2 password form and obtain a Bearer JWT access token.

### Protected Expenses (Requires Bearer Token)
- `POST /expenses` - Create an expense (automatically linked to current user).
- `GET /expenses` - List all expenses belonging to current user.
- `GET /expenses/{expense_id}` - Get a specific expense by ID (only if owned by current user).
- `PUT /expenses/{expense_id}` - Update a specific expense (only if owned by current user).
- `DELETE /expenses/{expense_id}` - Delete a specific expense (only if owned by current user).
- `GET /expenses/total` - Get total expense amount for current user.
- `GET /expenses/category-summary` - Get spending breakdown by category for current user.

### Health
- `GET /` - Health check.

## Using Swagger UI (/docs)

1. Open `http://127.0.0.1:8000/docs`.
2. Register a user under `POST /auth/signup`.
3. Click the green **Authorize** button at the top right.
4. Enter your registered email into **username** and your password into **password** (or paste your Bearer token).
5. Click **Authorize** then **Close**. All protected endpoints will now include the Bearer token automatically!

## Run Tests

Run the complete test suite:

```bash
python -m pytest -v
```
