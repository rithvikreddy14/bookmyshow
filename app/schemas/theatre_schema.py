from pydantic import BaseModel
from typing import List, Optional

# --- Screen Schemas ---
class ScreenBase(BaseModel):
    screen_name: str
    total_capacity: int

class ScreenCreate(ScreenBase):
    pass

class ScreenResponse(ScreenBase):
    id: int
    theatre_id: int

    class Config:
        from_attributes = True

# --- Theatre Schemas ---
class TheatreBase(BaseModel):
    theatre_name: str
    city: str
    location_address: str

class TheatreCreate(TheatreBase):
    pass

class TheatreResponse(TheatreBase):
    id: int
    screens: List[ScreenResponse] = []

    class Config:
        from_attributes = True