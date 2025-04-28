from fastapi import FastAPI, HTTPException, status
from typing import List
from pydantic import BaseModel
from books.models import BookCreate, BookResponse
from books.database import books_db, book_counter

app = FastAPI(
    title="Books Service",
    description="Управление книгами",
    version="1.0.0",
)


@app.get("/books", response_model=List[BookResponse])
def get_all_books():
    return books_db


@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    for book in books_db:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")


@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def add_book(book: BookCreate):
    global book_counter
    book_counter += 1
    new_book = BookResponse(id=book_counter, **book.dict())
    books_db.append(new_book)
    return new_book


@app.put("/books/{book_id}", response_model=BookResponse)
def replace_book(book_id: int, book_data: BookCreate):
    for book in books_db:
        if book.id == book_id:
            book.title = book_data.title
            book.author = book_data.author
            book.year = book_data.year
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")


class StatusUpdate(BaseModel):
    status: str

@app.patch("/books/{book_id}/status", response_model=BookResponse)
def update_book_status(book_id: int, payload: StatusUpdate):
    for book in books_db:
        if book.id == book_id:
            book.status = payload.status
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    global books_db
    books_db = [b for b in books_db if b.id != book_id]
    return
