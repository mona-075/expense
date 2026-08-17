from fastapi import Depends, FastAPI, status
from sqlalchemy.orm import Session

from crud import (
    create_expense,
    delete_expense,
    get_all_expenses,
    get_category_summary,
    get_expense,
    get_total_expenses,
    update_expense,
)
from database import Base, engine, get_db
from schemas import (
    CategorySummary,
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate,
    TotalExpenseResponse,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Expense Management API",
    description="Manage daily expenses with a clean FastAPI backend.",
    version="1.0.0",
    docs_url="/docs",
)


@app.get("/")
def home():
    return {"message": "Expense Management API is running!"}


@app.post("/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_new_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    return create_expense(db, expense)


@app.get("/expenses", response_model=list[ExpenseResponse])
def read_expenses(db: Session = Depends(get_db)):
    return get_all_expenses(db)


@app.get("/expenses/total", response_model=TotalExpenseResponse)
def total_expenses(db: Session = Depends(get_db)):
    return get_total_expenses(db)


@app.get("/expenses/category-summary", response_model=list[CategorySummary])
def category_summary(db: Session = Depends(get_db)):
    return get_category_summary(db)


@app.get("/expenses/{expense_id}", response_model=ExpenseResponse)
def read_expense(expense_id: int, db: Session = Depends(get_db)):
    return get_expense(db, expense_id)


@app.put("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_existing_expense(
    expense_id: int,
    expense: ExpenseUpdate,
    db: Session = Depends(get_db),
):
    return update_expense(db, expense_id, expense)


@app.delete("/expenses/{expense_id}")
def delete_existing_expense(expense_id: int, db: Session = Depends(get_db)):
    delete_expense(db, expense_id)
    return {"detail": "Expense deleted successfully"}

