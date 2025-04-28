from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RentalCreate(BaseModel):
    book_id: int
    user_id: int

class RentalResponse(RentalCreate):
    id: int
    rental_date: datetime
    return_date: Optional[datetime] = None
