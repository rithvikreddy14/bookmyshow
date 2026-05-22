from pydantic import BaseModel
from typing import List

class BookingCreate(BaseModel):
    show_id: int
    seat_ids: List[int] # Expecting a list of show_seat_ids

class BookingResponse(BaseModel):
    booking_id: int
    total_amount: float
    message: str