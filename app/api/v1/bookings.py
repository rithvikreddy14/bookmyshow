from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from datetime import datetime
from app.db.database import get_db
from app.db.models import ShowSeat, Booking, BookingSeat, User
from app.schemas.booking_schema import BookingCreate, BookingResponse
from app.api.dependencies import get_current_user

router = APIRouter()

@router.post("/book", response_model=BookingResponse, status_code=status.HTTP_200_OK)
def book_seats(booking_req: BookingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        # 1. Pessimistic Locking: Lock the requested rows immediately
        # nowait=True ensures that if someone else is currently locking these rows, it fails instantly
        seats = db.query(ShowSeat).filter(
            ShowSeat.id.in_(booking_req.seat_ids),
            ShowSeat.show_id == booking_req.show_id
        ).with_for_update(nowait=True).all()

        # 2. Validate existence
        if len(seats) != len(booking_req.seat_ids):
            raise HTTPException(status_code=404, detail="One or more seats not found for this show.")

        # 3. Check availability status
        for seat in seats:
            if seat.status != 'Available':
                raise HTTPException(status_code=400, detail=f"Seat ID {seat.id} is already {seat.status.lower()}.")

        # 4. Calculate total price dynamically
        total_price = sum([seat.price for seat in seats])

        # 5. Generate the Pending Booking Invoice
        new_booking = Booking(
            user_id=current_user.id,
            show_id=booking_req.show_id,
            booking_status='Pending',
            total_amount=total_price
        )
        db.add(new_booking)
        db.flush() # Flushes to DB to generate the booking ID, but does not commit yet

        # 6. Update Seat Status and map to BookingSeats
        booking_seats_to_insert = []
        for seat in seats:
            seat.status = 'Locked'
            seat.locked_at = datetime.utcnow()
            booking_seats_to_insert.append(
                BookingSeat(booking_id=new_booking.id, show_seat_id=seat.id)
            )

        db.bulk_save_objects(booking_seats_to_insert)

        # 7. Commit the transaction (this releases the locks for other users)
        db.commit()
        db.refresh(new_booking)

        return {
            "message": "Seats locked successfully. You have 10 minutes to complete the payment.",
            "booking_id": new_booking.id,
            "total_amount": float(total_price)
        }

    except OperationalError:
        # Catch the database row-lock exception
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="High traffic: These seats are currently being processed by another user. Please select different seats."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))