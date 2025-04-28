# rentals/main.py

from fastapi import FastAPI, HTTPException
from rentals.models import RentalCreate, RentalResponse
from rentals.database import rentals_db
from books.database import books_db
from users.database import users_db
from datetime import datetime
import requests
import logging

# Локальный счётчик аренды
rental_counter = 0

app = FastAPI(
    title="Rentals Service",
    description="Аренда книг",
    version="1.0.0",
)

BOOKS_SERVICE = "http://localhost:8000"
USERS_SERVICE = "http://localhost:8001"

# Настроим логирование стектрейсов
logging.basicConfig(level=logging.INFO)

@app.post("/rentals", response_model=RentalResponse, status_code=201)
def rent_book(rental: RentalCreate):
    global rental_counter
    try:
        # 1. Проверка книги по внешнему сервису
        book_resp = requests.get(f"{BOOKS_SERVICE}/books/{rental.book_id}", timeout=3)
        if book_resp.status_code == 404:
            raise HTTPException(404, "Книга не найдена")
        book_resp.raise_for_status()
        book = book_resp.json()

        if book.get("status") != "available":
            raise HTTPException(400, "Книга уже арендована")

        # 2. Проверка пользователя по внешнему сервису
        user_resp = requests.get(f"{USERS_SERVICE}/users/{rental.user_id}", timeout=3)
        if user_resp.status_code == 404:
            raise HTTPException(404, "Пользователь не найден")
        user_resp.raise_for_status()

        # 3. Создаём аренду
        rental_counter += 1
        new_rental = RentalResponse(
            id=rental_counter,
            rental_date=datetime.now(),
            **rental.dict()
        )
        rentals_db.append(new_rental)

        # 4. Обновляем статус книги в Books Service
        patch_resp = requests.patch(
            f"{BOOKS_SERVICE}/books/{rental.book_id}/status",
            json={"status": "rented"},
            timeout=3
        )
        if not patch_resp.ok:
            # Откат: удаляем созданную аренду
            rentals_db.pop()
            raise HTTPException(500, "Не удалось обновить статус книги")

        return new_rental

    except HTTPException:
        # Перебросим наши HTTPException дальше
        raise
    except Exception as exc:
        logging.exception("Ошибка при создании аренды")
        raise HTTPException(500, detail="Внутренняя ошибка сервиса аренды") from exc


@app.put("/rentals/{rental_id}/return", response_model=RentalResponse)
def return_book(rental_id: int):
    rental = next((r for r in rentals_db if r.id == rental_id), None)
    if not rental:
        raise HTTPException(404, "Аренда не найдена")

    if rental.return_date:
        raise HTTPException(400, "Книга уже возвращена")

    rental.return_date = datetime.now()

    # Сбрасываем статус книги
    try:
        # Сначала проверяем, что книга существует
        book_resp = requests.get(f"{BOOKS_SERVICE}/books/{rental.book_id}", timeout=3)
        book_resp.raise_for_status()
        # Обновляем статус обратно
        requests.patch(
            f"{BOOKS_SERVICE}/books/{rental.book_id}/status",
            json={"status": "available"},
            timeout=3
        )
    except Exception:
        # Логируем, но не ломаем возврат аренды
        logging.exception("Не удалось вернуть статус книги")

    return rental
