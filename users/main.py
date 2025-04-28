from fastapi import FastAPI, HTTPException
from typing import List
from users.models import UserCreate, UserResponse
from users.database import users_db, user_counter
from datetime import datetime

app = FastAPI(
    title="Users Service",
    description="Управление пользователями",
    version="1.0.0",
)

# Эндпоинты для пользователей
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    """Зарегистрировать нового пользователя"""
    global user_counter
    # Проверка уникальности email
    for u in users_db:
        if u.email == user.email:
            raise HTTPException(
                status_code=400,
                detail="Email уже зарегистрирован"
            )
    
    user_counter += 1
    new_user = UserResponse(
        id=user_counter,
        registration_date=datetime.now(),
        **user.dict()
    )
    users_db.append(new_user)
    return new_user

@app.get("/users", response_model=List[UserResponse])
def get_all_users():
    """Получить всех пользователей"""
    return users_db


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")