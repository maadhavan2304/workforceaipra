from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.deps import get_current_user, require_roles
from app.models.user import User
from app.schemas.auth import UserCreate, UserOut, Token, LoginRequest, RefreshRequest

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(
    payload: UserCreate,
    db: Session = Depends(get_db),
    # Only Admin/HR can create new user accounts
    current_user: User = Depends(require_roles("Admin", "HR")),
):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        employee_id=payload.employee_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/bootstrap-admin", response_model=UserOut, status_code=201)
def bootstrap_admin(payload: UserCreate, db: Session = Depends(get_db)):
    """One-time endpoint to create the first Admin account when no users exist yet."""
    if db.query(User).count() > 0:
        raise HTTPException(status_code=403, detail="Admin bootstrap already completed")
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role="Admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    access_token = create_access_token(subject=str(user.id), role=user.role.value)
    refresh_token = create_refresh_token(subject=str(user.id))
    return Token(access_token=access_token, refresh_token=refresh_token, user=user)


@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    data = decode_token(payload.refresh_token)
    if not data or data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = db.query(User).filter(User.id == int(data["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = create_access_token(subject=str(user.id), role=user.role.value)
    new_refresh = create_refresh_token(subject=str(user.id))
    return Token(access_token=access_token, refresh_token=new_refresh, user=user)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
