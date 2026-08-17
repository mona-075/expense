from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Expense
from schemas import ExpenseCreate, ExpenseUpdate


def create_expense(db: Session, expense: ExpenseCreate) -> Expense:
    db_expense = Expense(**expense.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_all_expenses(db: Session):
    return db.query(Expense).order_by(Expense.date.desc()).all()


def get_expense(db: Session, expense_id: int) -> Expense:
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )
    return expense


def update_expense(db: Session, expense_id: int, expense_update: ExpenseUpdate) -> Expense:
    expense = get_expense(db, expense_id)

    for key, value in expense_update.model_dump(exclude_unset=True).items():
        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense_id: int) -> None:
    expense = get_expense(db, expense_id)
    db.delete(expense)
    db.commit()


def get_total_expenses(db: Session) -> dict[str, float]:
    total = db.query(func.coalesce(func.sum(Expense.amount), 0)).scalar() or 0
    return {"total_expenses": round(float(total), 2)}


def get_category_summary(db: Session) -> list[dict[str, Any]]:
    rows = (
        db.query(Expense.category, func.sum(Expense.amount).label("total_amount"))
        .group_by(Expense.category)
        .all()
    )
    return [
        {"category": category, "total_amount": round(float(total), 2)}
        for category, total in rows
    ]
