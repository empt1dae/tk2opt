from pydantic import BaseModel


class BookCreate(BaseModel):
    title: str
    author: str
    year: int

class BookResponse(BookCreate):
    id: int
    status: str = "available"