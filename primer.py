from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(
    title="Библиотека API",
    description="API для управления книгами, пользователями и арендой",
    version="1.0.0",
    openapi_tags=[
        {"name": "Книги", "description": "Операции с книгами"},
        {"name": "Пользователи", "description": "Управление пользователями"},
        {"name": "Аренда", "description": "Операции аренды книг"},
    ],
)

# Временные "базы данных" и счетчики
books_db = []
users_db = []
rentals_db = []
book_counter = 0
user_counter = 0
rental_counter = 0

# Модели данных
class BookCreate(BaseModel):
    title: str
    author: str
    year: int

class BookResponse(BookCreate):
    id: int
    status: str = "available"

class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(UserCreate):
    id: int
    registration_date: datetime

class RentalCreate(BaseModel):
    book_id: int
    user_id: int

class RentalResponse(RentalCreate):
    id: int
    rental_date: datetime
    return_date: Optional[datetime] = None

# Эндпоинты для книг
@app.get("/books", response_model=List[BookResponse], tags=["Книги"])
def get_all_books():
    """Получить список всех книг"""
    return books_db

@app.get("/books/{book_id}", response_model=BookResponse, tags=["Книги"])
def get_book(book_id: int):
    """Получить книгу по ID"""
    # Прямой поиск книги в списке
    for book in books_db:
        if book.id == book_id:
            return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Книга не найдена"
    )

@app.post("/books", response_model=BookResponse, status_code=201, tags=["Книги"])
def add_book(book: BookCreate):
    """Добавить новую книгу"""
    global book_counter
    book_counter += 1
    new_book = BookResponse(id=book_counter, **book.dict())
    books_db.append(new_book)
    return new_book

@app.put("/books/{book_id}", response_model=BookResponse, tags=["Книги"])
def update_book(book_id: int, book_data: BookCreate):
    """Обновить информацию о книге"""
    # Поиск и обновление книги
    for book in books_db:
        if book.id == book_id:
            book.title = book_data.title
            book.author = book_data.author
            book.year = book_data.year
            return book
    raise HTTPException(status_code=404, detail="Книга не найдена")

@app.delete("/books/{book_id}", status_code=204, tags=["Книги"])
def delete_book(book_id: int):
    """Удалить книгу"""
    global books_db
    # Фильтрация списка без использования вспомогательной функции
    books_db = [b for b in books_db if b.id != book_id]
    return

# Эндпоинты для пользователей
@app.post("/users", response_model=UserResponse, status_code=201, tags=["Пользователи"])
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

@app.get("/users", response_model=List[UserResponse], tags=["Пользователи"])
def get_all_users():
    """Получить всех пользователей"""
    return users_db

# Эндпоинты для аренды
@app.post("/rentals", response_model=RentalResponse, status_code=201, tags=["Аренда"])
def rent_book(rental: RentalCreate):
    """Взять книгу в аренду"""
    global rental_counter
    
    # Поиск книги
    book = None
    for b in books_db:
        if b.id == rental.book_id:
            book = b
            break
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    
    # Поиск пользователя
    user = None
    for u in users_db:
        if u.id == rental.user_id:
            user = u
            break
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if book.status != "available":
        raise HTTPException(status_code=400, detail="Книга уже арендована")
    
    rental_counter += 1
    new_rental = RentalResponse(
        id=rental_counter,
        rental_date=datetime.now(),
        **rental.dict()
    )
    rentals_db.append(new_rental)
    book.status = "rented"
    return new_rental

@app.put("/rentals/{rental_id}/return", response_model=RentalResponse, tags=["Аренда"])
def return_book(rental_id: int):
    """Вернуть книгу"""
    # Поиск аренды
    rental = None
    for r in rentals_db:
        if r.id == rental_id:
            rental = r
            break
    if not rental:
        raise HTTPException(status_code=404, detail="Аренда не найдена")
    
    if rental.return_date:
        raise HTTPException(status_code=400, detail="Книга уже возвращена")
    
    rental.return_date = datetime.now()
    
    # Поиск и обновление книги
    for b in books_db:
        if b.id == rental.book_id:
            b.status = "available"
            break
    
    return rental