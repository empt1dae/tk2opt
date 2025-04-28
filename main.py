from fastapi import FastAPI
from book import router as book_router
from user import router as user_router
from rental import router as rental_router

app = FastAPI(
    title="Библиотека API",
    description="API для управления книгами, пользователями и арендой",
    version="1.0.0",
)

app.include_router(book_router)
app.include_router(user_router)
app.include_router(rental_router)


