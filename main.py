from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from crud import (
    create_expense,
    create_user,
    delete_expense,
    get_all_expenses,
    get_category_summary,
    get_expense,
    get_total_expenses,
    get_user_by_email,
    update_expense,
)
from database import Base, engine, get_db
from models import User
from schemas import (
    CategorySummary,
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate,
    Token,
    TotalExpenseResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Expense Management API",
    description="Manage daily expenses with user authentication and authorization using FastAPI and JWT.",
    version="1.0.0",
    docs_url="/docs",
)


# --- Root / Health ---
@app.get("/", tags=["Health"])
def home():
    return {"message": "Expense Management API is running!"}


# --- Authentication Endpoints ---
@app.post(
    "/auth/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user_data.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    hashed_password = get_password_hash(user_data.password)
    return create_user(db, user=user_data, hashed_password=hashed_password)


@app.post(
    "/auth/login",
    response_model=Token,
    tags=["Authentication"],
)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    user = get_user_by_email(db, email=user_data.email)
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# --- Protected Expense Endpoints ---
@app.post(
    "/expenses",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Expenses"],
)
def create_new_expense(
    expense: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_expense(db, expense=expense, user_id=current_user.id)


@app.get(
    "/expenses",
    response_model=list[ExpenseResponse],
    tags=["Expenses"],
)
def read_expenses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_all_expenses(db, user_id=current_user.id)


@app.get(
    "/expenses/total",
    response_model=TotalExpenseResponse,
    tags=["Expenses"],
)
def total_expenses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_total_expenses(db, user_id=current_user.id)


@app.get(
    "/expenses/category-summary",
    response_model=list[CategorySummary],
    tags=["Expenses"],
)
def category_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_category_summary(db, user_id=current_user.id)


@app.get(
    "/expenses/{expense_id}",
    response_model=ExpenseResponse,
    tags=["Expenses"],
)
def read_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_expense(db, expense_id=expense_id, user_id=current_user.id)


@app.put(
    "/expenses/{expense_id}",
    response_model=ExpenseResponse,
    tags=["Expenses"],
)
def update_existing_expense(
    expense_id: int,
    expense: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_expense(
        db,
        expense_id=expense_id,
        expense_update=expense,
        user_id=current_user.id,
    )


@app.delete(
    "/expenses/{expense_id}",
    tags=["Expenses"],
)
def delete_existing_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_expense(db, expense_id=expense_id, user_id=current_user.id)
    return {"detail": "Expense deleted successfully"}

