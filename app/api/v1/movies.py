from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import Movie, User
from app.schemas.movie_schema import MovieCreate, MovieResponse
from app.api.dependencies import RoleChecker

router = APIRouter()

# Define who can add movies
allow_admins = RoleChecker(["SuperAdmin", "TheatreAdmin"])

@router.post("/", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
def create_movie(movie: MovieCreate, db: Session = Depends(get_db), current_user: User = Depends(allow_admins)):
    new_movie = Movie(**movie.model_dump())
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie

@router.get("/", response_model=List[MovieResponse])
def get_movies(db: Session = Depends(get_db)):
    return db.query(Movie).all()