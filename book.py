from fastapi import APIRouter, HTTPException, status
from typing import List
from model import BookCreate, BookResponse

router = APIRouter()

books_db = []
book_counter = 0

@router.get("/books", response_model=List[BookResponse], tags=["Книги"])
def get_all_books():
    return books_db

@router.get("/books/{book_id}", response_model=BookResponse, tags=["Книги"])
def get_book(book_id: int):
    for book in books_db:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")

@router.post("/books", response_model=BookResponse, status_code=201, tags=["Книги"])
def add_book(book: BookCreate):
    global book_counter
    book_counter += 1
    new_book = BookResponse(id=book_counter, **book.dict())
    books_db.append(new_book)
    return new_book

@router.put("/books/{book_id}", response_model=BookResponse, tags=["Книги"])
def update_book(book_id: int, book_data: BookCreate):
    for book in books_db:
        if book.id == book_id:
            book.title = book_data.title
            book.author = book_data.author
            book.year = book_data.year
            return book
    raise HTTPException(status_code=404, detail="Книга не найдена")

@router.delete("/books/{book_id}", status_code=204, tags=["Книги"])
def delete_book(book_id: int):
    global books_db
    books_db = [b for b in books_db if b.id != book_id]
    return
