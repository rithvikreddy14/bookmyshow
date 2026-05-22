from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from datetime import datetime, timedelta
from app.db.database import get_db
from app.db.models import ShowSeat, Booking, BookingSeat, User
from app.schemas.booking_schema import BookingCreate, BookingResponse
from app.api.dependencies import get_current_user
import uuid 
from app.schemas.booking_schema import PaymentResponse
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
        expiration_limit = datetime.utcnow() - timedelta(minutes=10)

        for seat in seats:
            if seat.status == 'Booked':
                raise HTTPException(status_code=400, detail=f"Seat ID {seat.id} is already permanently booked.")
            
            if seat.status == 'Locked':
                # If it's locked, check if the lock is still valid (less than 10 mins old)
                if seat.locked_at and seat.locked_at > expiration_limit:
                    raise HTTPException(status_code=400, detail=f"Seat ID {seat.id} is currently locked by another user.")

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
    
@router.post("/{booking_id}/pay", response_model=PaymentResponse, status_code=status.HTTP_200_OK)
def simulate_payment(booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1. Fetch the booking and verify ownership
    booking = db.query(Booking).filter(
        Booking.id == booking_id, 
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
        
    # 2. Prevent double payments
    if booking.booking_status == 'Confirmed':
        raise HTTPException(status_code=400, detail="This booking has already been paid for.")
        
    if booking.booking_status == 'Cancelled':
        raise HTTPException(status_code=400, detail="This booking was cancelled.")

    # 3. Process the "Payment" and update the booking invoice
    booking.booking_status = 'Confirmed'
    
    # 4. Convert the physical seats from 'Locked' to 'Booked'
    for booking_seat in booking.booking_seats:
        show_seat = booking_seat.show_seat
        show_seat.status = 'Booked'
        
    # 5. Generate a fake bank transaction ID
    transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
    
    # 6. Commit the finalized transaction to the database
    db.commit()
    
    return {
        "booking_id": booking.id,
        "transaction_id": transaction_id,
        "status": "Confirmed",
        "message": "Payment successful! Your tickets are confirmed."
    }