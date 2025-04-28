from fastapi import APIRouter, HTTPException
from model import RentalCreate, RentalResponse
from datetime import datetime

router = APIRouter()

rentals_db = []
rental_counter = 0

# Для обращения к книгам и пользователям
from book import books_db
from user import users_db

@router.post("/rentals", response_model=RentalResponse, status_code=201, tags=["Аренда"])
def rent_book(rental: RentalCreate):
    global rental_counter

    book = next((b for b in books_db if b.id == rental.book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    
    user = next((u for u in users_db if u.id == rental.user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if book.status != "available":
        raise HTTPException(status_code=400, detail="Книга уже арендована")
    
    rental_counter += 1
    new_rental = RentalResponse(id=rental_counter, rental_date=datetime.now(), **rental.dict())
    rentals_db.append(new_rental)
    book.status = "rented"
    return new_rental

@router.put("/rentals/{rental_id}/return", response_model=RentalResponse, tags=["Аренда"])
def return_book(rental_id: int):
    rental = next((r for r in rentals_db if r.id == rental_id), None)
    if not rental:
        raise HTTPException(status_code=404, detail="Аренда не найдена")
    
    if rental.return_date:
        raise HTTPException(status_code=400, detail="Книга уже возвращена")
    
    rental.return_date = datetime.now()

    for b in books_db:
        if b.id == rental.book_id:
            b.status = "available"
            break
    
    return rental
