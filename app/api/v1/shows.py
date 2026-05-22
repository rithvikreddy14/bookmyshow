from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import Show, Movie, Screen, User
from app.schemas.show_schema import ShowCreate, ShowResponse
from app.api.dependencies import RoleChecker

router = APIRouter()
allow_admins = RoleChecker(["SuperAdmin", "TheatreAdmin"])

@router.post("/", response_model=ShowResponse, status_code=status.HTTP_201_CREATED)
def create_show(show: ShowCreate, db: Session = Depends(get_db), current_user: User = Depends(allow_admins)):
    # 1. Verify the Movie exists
    if not db.query(Movie).filter(Movie.id == show.movie_id).first():
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # 2. Verify the Screen exists
    if not db.query(Screen).filter(Screen.id == show.screen_id).first():
        raise HTTPException(status_code=404, detail="Screen not found")

    # 3. Prevent Overlapping Shows (The Business Logic)
    overlapping_show = db.query(Show).filter(
        Show.screen_id == show.screen_id,
        Show.show_date == show.show_date,
        Show.start_time < show.end_time,  # New show starts before existing show ends
        Show.end_time > show.start_time   # New show ends after existing show starts
    ).first()

    if overlapping_show:
        raise HTTPException(status_code=400, detail="A show is already scheduled on this screen during this time.")

    # 4. Create the Show
    new_show = Show(**show.model_dump())
    db.add(new_show)
    db.commit()
    db.refresh(new_show)
    return new_show

@router.get("/", response_model=List[ShowResponse])
def get_shows(movie_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Show)
    if movie_id:
        query = query.filter(Show.movie_id == movie_id)
    return query.all()