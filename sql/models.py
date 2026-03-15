from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, VARCHAR, Boolean, ForeignKey
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from fastapi.exceptions import HTTPException

class LogIn(BaseModel):
    user_name: str
    password: str

class UpdateData(BaseModel):
    user_name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    role: Optional[str] = None

class UserFilter(BaseModel):
    id: Optional[int] = None
    user_name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    role: Optional[str] = None
    limit: int = 10
    offset: int = 0

class CreateUser(BaseModel):
    user_name: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=5, max_length=15)
    title: str = Field(min_length=4, max_length=15)
    description: str = Field(min_length=4, max_length=15)
    completed: bool = False
    role: Optional[str] = "user"

    @field_validator("password")
    def safety_check(cls, password):
        if any([letter.isupper() for letter in password]) and any([letter.isdigit()  for letter in password]):
            return password

        raise HTTPException(status_code=401,
                            detail="Password is unsafe, please use numbers, and high register letters")




class Base(DeclarativeBase):
    pass

class Protected(Base):
    __tablename__ = 'data_protected_table'

    id: Mapped[int] = mapped_column(ForeignKey("test_api_sql.id"), nullable=False, autoincrement=True, primary_key=True)
    password: Mapped[str] = mapped_column(VARCHAR(150))
    user_name: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    role: Mapped[str] = mapped_column(VARCHAR(20))


class User(Base):
    __tablename__ = 'test_api_sql'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_name: Mapped[str] = mapped_column(VARCHAR(20))
    title: Mapped[str] = mapped_column(VARCHAR(20))
    description: Mapped[str] = mapped_column(VARCHAR(30))
    completed: Mapped[bool] = mapped_column(Boolean)
    role: Mapped[str] = mapped_column(VARCHAR(20))

