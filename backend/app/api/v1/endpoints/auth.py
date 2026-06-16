from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_password_hash, get_current_user
from app.core.config import settings
from app.models.models import Usuario
from app.schemas.schemas import Token, UserCreate, UserResponse

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(Usuario).filter(Usuario.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = create_access_token(
        data={"sub": user.username, "roles": [user.rol]},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existente = db.query(Usuario).filter(
        (Usuario.username == user.username) | (Usuario.email == user.email)
    ).first()

    if existente:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    hashed = get_password_hash(user.password)

    db_user = Usuario(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        rol=user.rol,
        hashed_password=hashed
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user = db.query(Usuario).filter(Usuario.username == current_user.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
