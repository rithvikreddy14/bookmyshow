from pydantic import BaseModel
from datetime import date, datetime

class ShowBase(BaseModel):
    movie_id: int
    screen_id: int
    show_date: date
    start_time: datetime
    end_time: datetime

class ShowCreate(ShowBase):
    pass

class ShowResponse(ShowBase):
    id: int

    class Config:
        from_attributes = True

class ShowSeatMapResponse(BaseModel):
    id: int
    show_id: int
    seat_id: int
    price: float
    status: str
    row_identifier: str
    seat_number: int
    seat_type: str

    class Config:
        from_attributes = True