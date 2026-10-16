
import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app import models

from app.schemas import (
    UserRegister,
    UserLogin,
    InternshipCreate,
    InternshipResponse,
    InternshipUpdate,
)


# Load environment variables from .env
load_dotenv()

app = FastAPI()

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing from .env")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()
security = HTTPBearer()


# Create JWT access token
def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# Verify token and retrieve the logged-in user
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        user_id = int(payload["sub"])

    except (InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(models.User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# Create database tables
if os.getenv("APP_ENV") != "test":
    Base.metadata.create_all(bind=engine)


# Home endpoint
@app.get("/")
def home():
    return {"message": "Internship Tracker API is running"}


# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Register a new user
@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(models.User)
        .filter(models.User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    hashed_password = password_hash.hash(user_data.password)

    new_user = models.User(
        email=str(user_data.email),
        hashed_password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
        },
    }


# Log in and generate access token
@app.post("/login")
def login_user(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    user = (
        db.query(models.User)
        .filter(models.User.email == user_data.email)
        .first()
    )

    if user is None or not password_hash.verify(
        user_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# Get the currently logged-in user's profile
@app.get("/me")
def read_current_user(
    current_user: models.User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "email": current_user.email,
    }



@app.post(
    "/internships",
    response_model=InternshipResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_internship(
    internship_data: InternshipCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    new_internship = models.Internship(
        company=internship_data.company,
        role=internship_data.role,
        status=internship_data.status,
        application_date=internship_data.application_date,
        user_id=current_user.id,
    )

    db.add(new_internship)
    db.commit()
    db.refresh(new_internship)

    return new_internship




@app.get("/internships", response_model=list[InternshipResponse])
def list_internships(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    internships = (
        db.query(models.Internship)
        .filter(models.Internship.user_id == current_user.id)
        .all()
    )
    return internships



@app.get("/internships/{internship_id}", response_model=InternshipResponse)
def get_internship(
    internship_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    internship = (
        db.query(models.Internship)
        .filter(
            models.Internship.id == internship_id,
            models.Internship.user_id == current_user.id,
        )
        .first()
    )

    if internship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Internship not found",
        )

    return internship


from app.schemas import (
    UserRegister,
    UserLogin,
    InternshipCreate,
    InternshipResponse,
    InternshipUpdate,
)


@app.put(
    "/internships/{internship_id}",
    response_model=InternshipResponse,
)
def update_internship(
    internship_id: int,
    internship_data: InternshipUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    internship = (
        db.query(models.Internship)
        .filter(
            models.Internship.id == internship_id,
            models.Internship.user_id == current_user.id,
        )
        .first()
    )

    if internship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Internship not found",
        )

    internship.company = internship_data.company
    internship.role = internship_data.role
    internship.status = internship_data.status
    internship.application_date = internship_data.application_date

    db.commit()
    db.refresh(internship)

    return internship








@app.delete("/internships/{internship_id}")
def delete_internship(
    internship_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    internship = (
        db.query(models.Internship)
        .filter(
            models.Internship.id == internship_id,
            models.Internship.user_id == current_user.id,
        )
        .first()
    )

    if internship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Internship not found",
        )

    db.delete(internship)
    db.commit()

    return {"message": "Internship deleted successfully"}
