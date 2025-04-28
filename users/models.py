from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(UserCreate):
    id: int
    registration_date: datetime
