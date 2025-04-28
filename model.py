from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# Модели книг
class BookCreate(BaseModel):
    title: str
    author: str
    year: int

class BookResponse(BookCreate):
    id: int
    status: str = "available"

# Модели пользователей
class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(UserCreate):
    id: int
    registration_date: datetime

# Модели аренды
class RentalCreate(BaseModel):
    book_id: int
    user_id: int

class RentalResponse(RentalCreate):
    id: int
    rental_date: datetime
    return_date: Optional[datetime] = None
