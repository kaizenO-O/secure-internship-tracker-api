
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class InternshipCreate(BaseModel):
    company: str = Field(min_length=1, max_length=150)
    role: str = Field(min_length=1, max_length=150)
    status: Literal[
        "Applied",
        "Interview",
        "Offer",
        "Rejected",
        "Withdrawn",
    ] = "Applied"
    application_date: date


class InternshipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company: str
    role: str
    status: str
    application_date: date
    user_id: int


class InternshipUpdate(BaseModel):
    company: str = Field(min_length=1, max_length=150)
    role: str = Field(min_length=1, max_length=150)
    status: Literal[
        "Applied",
        "Interview",
        "Offer",
        "Rejected",
        "Withdrawn",
    ]
    application_date: date
