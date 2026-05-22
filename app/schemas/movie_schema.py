from pydantic import BaseModel
from typing import Optional
from datetime import date

class MovieBase(BaseModel):
    title: str
    language: Optional[str] = None
    genre: Optional[str] = None
    duration_mins: Optional[int] = None
    release_date: Optional[date] = None

class MovieCreate(MovieBase):
    pass

class MovieResponse(MovieBase):
    id: int

    class Config:
        from_attributes = True