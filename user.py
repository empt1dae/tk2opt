from fastapi import APIRouter, HTTPException
from typing import List
from model import UserCreate, UserResponse
from datetime import datetime

router = APIRouter()

users_db = []
user_counter = 0

@router.post("/users", response_model=UserResponse, status_code=201, tags=["Пользователи"])
def create_user(user: UserCreate):
    global user_counter
    for u in users_db:
        if u.email == user.email:
            raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    user_counter += 1
    new_user = UserResponse(id=user_counter, registration_date=datetime.now(), **user.dict())
    users_db.append(new_user)
    return new_user

@router.get("/users", response_model=List[UserResponse], tags=["Пользователи"])
def get_all_users():
    return users_db
