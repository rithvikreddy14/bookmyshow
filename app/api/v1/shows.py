from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import Show, Movie, Screen, User, Seat, ShowSeat
from app.schemas.show_schema import ShowCreate, ShowResponse
from app.api.dependencies import RoleChecker
from app.schemas.show_schema import ShowSeatMapResponse

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

    # 3. Prevent Overlapping Shows
    overlapping_show = db.query(Show).filter(
        Show.screen_id == show.screen_id,
        Show.show_date == show.show_date,
        Show.start_time < show.end_time,  
        Show.end_time > show.start_time   
    ).first()

    if overlapping_show:
        raise HTTPException(status_code=400, detail="A show is already scheduled on this screen during this time.")

    # 4. Create the Show
    new_show = Show(**show.model_dump())
    db.add(new_show)
    db.commit()
    db.refresh(new_show)

    # 5. Generate Dynamic Seat Inventory
    # Fetch all physical seats belonging to this screen
    screen_seats = db.query(Seat).filter(Seat.screen_id == show.screen_id).all()
    
    show_seats_to_insert = []
    for seat in screen_seats:
        # Dynamic pricing logic: Premium seats cost more
        seat_price = 250.00 if seat.seat_type == 'Premium' else 150.00
        
        show_seats_to_insert.append(
            ShowSeat(
                show_id=new_show.id,
                seat_id=seat.id,
                price=seat_price,
                status='Available'
            )
        )
    
    # Bulk insert for maximum performance
    if show_seats_to_insert:
        db.bulk_save_objects(show_seats_to_insert)
        db.commit()

    return new_show

@router.get("/", response_model=List[ShowResponse])
def get_shows(movie_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Show)
    if movie_id:
        query = query.filter(Show.movie_id == movie_id)
    return query.all()

@router.get("/{show_id}/seats", response_model=List[ShowSeatMapResponse])
def get_show_seat_map(show_id: int, db: Session = Depends(get_db)):
    # 1. Verify the Show exists
    show = db.query(Show).filter(Show.id == show_id).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")

    # 2. Perform an SQL JOIN to merge real-time status with physical layout
    seat_map = db.query(
        ShowSeat.id,
        ShowSeat.show_id,
        ShowSeat.seat_id,
        ShowSeat.price,
        ShowSeat.status,
        Seat.row_identifier,
        Seat.seat_number,
        Seat.seat_type
    ).join(Seat, ShowSeat.seat_id == Seat.id)\
     .filter(ShowSeat.show_id == show_id)\
     .all()

    # 3. Format the response
    formatted_seats = []
    for seat in seat_map:
        formatted_seats.append({
            "id": seat.id,
            "show_id": seat.show_id,
            "seat_id": seat.seat_id,
            "price": float(seat.price),
            "status": seat.status, # 'Available', 'Locked', or 'Booked'
            "row_identifier": seat.row_identifier,
            "seat_number": seat.seat_number,
            "seat_type": seat.seat_type
        })

    return formatted_seats