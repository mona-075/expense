# Expense Management API

A simple FastAPI project for tracking personal expenses.

## Features

- Create an expense
- Get all expenses
- Get a single expense by ID
- Update an expense
- Delete an expense
- Get total expenses
- Get category-wise spending
- Swagger UI at /docs
- PostgreSQL support via SQLAlchemy
- Environment-based configuration

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- Uvicorn
- Pytest

## Project Structure

```text
expense_management/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── crud.py
├── requirements.txt
├── .env.example
├── .env
├── .gitignore
├── README.md
└── tests/
```

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file from the example:

```bash
copy .env.example .env
```

Then update the database URL with your local PostgreSQL password:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/expense_db
```

4. Create the PostgreSQL database if needed:

```sql
CREATE DATABASE expense_db;
```

5. Run the API:

```bash
uvicorn main:app --reload
```

Open the Swagger docs here:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

- `GET /` - API status
- `POST /expenses` - Create an expense
- `GET /expenses` - Get all expenses
- `GET /expenses/{expense_id}` - Get one expense
- `PUT /expenses/{expense_id}` - Update an expense
- `DELETE /expenses/{expense_id}` - Delete an expense
- `GET /expenses/total` - Total expenses
- `GET /expenses/category-summary` - Category totals

## Example JSON for Creating an Expense

```json
{
  "title": "Groceries",
  "amount": 125.5,
  "category": "Food",
  "description": "Weekend shopping"
}
```

## Run Tests

```bash
pytest
```

## Notes

- `.env` is intentionally ignored by Git.
- The project uses a SQLite fallback on local tests if no PostgreSQL URL is set.
