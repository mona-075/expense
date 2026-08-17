from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Expense, User
from schemas import ExpenseCreate, ExpenseUpdate, UserCreate


# --- User CRUD ---
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserCreate, hashed_password: str) -> User:
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --- Expense CRUD (Scoped by user_id) ---
def create_expense(db: Session, expense: ExpenseCreate, user_id: int) -> Expense:
    db_expense = Expense(**expense.model_dump(), user_id=user_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_all_expenses(db: Session, user_id: int) -> list[Expense]:
    return (
        db.query(Expense)
        .filter(Expense.user_id == user_id)
        .order_by(Expense.date.desc())
        .all()
    )


def get_expense(db: Session, expense_id: int, user_id: int) -> Expense:
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.user_id == user_id)
        .first()
    )
    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )
    return expense


def update_expense(
    db: Session, expense_id: int, expense_update: ExpenseUpdate, user_id: int
) -> Expense:
    expense = get_expense(db, expense_id, user_id)

    for key, value in expense_update.model_dump(exclude_unset=True).items():
        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense_id: int, user_id: int) -> None:
    expense = get_expense(db, expense_id, user_id)
    db.delete(expense)
    db.commit()


def get_total_expenses(db: Session, user_id: int) -> dict[str, float]:
    total = (
        db.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(Expense.user_id == user_id)
        .scalar()
        or 0
    )
    return {"total_expenses": round(float(total), 2)}


def get_category_summary(db: Session, user_id: int) -> list[dict[str, Any]]:
    rows = (
        db.query(Expense.category, func.sum(Expense.amount).label("total_amount"))
        .filter(Expense.user_id == user_id)
        .group_by(Expense.category)
        .all()
    )
    return [
        {"category": category, "total_amount": round(float(total), 2)}
        for category, total in rows
    ]
