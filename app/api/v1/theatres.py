from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import Theatre, Screen, User
from app.schemas.theatre_schema import TheatreCreate, TheatreResponse, ScreenCreate, ScreenResponse
from app.api.dependencies import RoleChecker

router = APIRouter()

# Define who can modify theatres
allow_admins = RoleChecker(["SuperAdmin", "TheatreAdmin"])

@router.post("/", response_model=TheatreResponse, status_code=status.HTTP_201_CREATED)
def create_theatre(theatre: TheatreCreate, db: Session = Depends(get_db), current_user: User = Depends(allow_admins)):
    new_theatre = Theatre(**theatre.model_dump())
    db.add(new_theatre)
    db.commit()
    db.refresh(new_theatre)
    return new_theatre

@router.get("/", response_model=List[TheatreResponse])
def get_all_theatres(city: str = None, db: Session = Depends(get_db)):
    # Customers don't need a token to view theatres
    query = db.query(Theatre)
    if city:
        query = query.filter(Theatre.city.ilike(f"%{city}%"))
    return query.all()

@router.post("/{theatre_id}/screens", response_model=ScreenResponse, status_code=status.HTTP_201_CREATED)
def add_screen_to_theatre(theatre_id: int, screen: ScreenCreate, db: Session = Depends(get_db), current_user: User = Depends(allow_admins)):
    # Check if theatre exists
    theatre = db.query(Theatre).filter(Theatre.id == theatre_id).first()
    if not theatre:
        raise HTTPException(status_code=404, detail="Theatre not found")
    
    new_screen = Screen(**screen.model_dump(), theatre_id=theatre_id)
    db.add(new_screen)
    db.commit()
    db.refresh(new_screen)
    return new_screen