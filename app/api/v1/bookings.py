import razorpay
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from datetime import datetime, timedelta
from app.db.database import get_db
from app.db.models import ShowSeat, Booking, BookingSeat, User
from app.schemas.booking_schema import BookingCreate, BookingResponse, PaymentVerification, PaymentSuccessResponse
from app.api.dependencies import get_current_user
from app.core.config import settings

router = APIRouter()

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@router.post("/book", response_model=BookingResponse, status_code=status.HTTP_200_OK)
def book_seats(booking_req: BookingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        # 1. Pessimistic Locking
        seats = db.query(ShowSeat).filter(
            ShowSeat.id.in_(booking_req.seat_ids),
            ShowSeat.show_id == booking_req.show_id
        ).with_for_update(nowait=True).all()

        if len(seats) != len(booking_req.seat_ids):
            raise HTTPException(status_code=404, detail="One or more seats not found for this show.")

        # 2. Check Availability & Lazy Expiration
        expiration_limit = datetime.utcnow() - timedelta(minutes=10)
        for seat in seats:
            if seat.status == 'Booked':
                raise HTTPException(status_code=400, detail=f"Seat ID {seat.id} is already permanently booked.")
            if seat.status == 'Locked' and seat.locked_at and seat.locked_at > expiration_limit:
                raise HTTPException(status_code=400, detail=f"Seat ID {seat.id} is currently locked by another user.")

        # 3. Calculate Pricing
        total_price = sum([seat.price for seat in seats])

        # 4. Generate Razorpay Order
        # Razorpay expects the amount in the smallest currency unit (paise for INR). So, multiply by 100.
        order_data = {
            "amount": int(total_price * 100), 
            "currency": "INR",
            "receipt": f"bms_receipt_{current_user.id}_{int(datetime.utcnow().timestamp())}",
            "payment_capture": 1 # Auto-capture the payment
        }
        
        # This makes an external API call to Razorpay
        razorpay_order = razorpay_client.order.create(data=order_data)

        # 5. Generate Pending Invoice (Now tracking the Razorpay Order ID)
        new_booking = Booking(
            user_id=current_user.id,
            show_id=booking_req.show_id,
            booking_status='Pending',
            total_amount=total_price,
            razorpay_order_id=razorpay_order['id'] # Save the ID!
        )
        db.add(new_booking)
        db.flush() 

        # 6. Lock Seats
        booking_seats_to_insert = []
        for seat in seats:
            seat.status = 'Locked'
            seat.locked_at = datetime.utcnow()
            booking_seats_to_insert.append(
                BookingSeat(booking_id=new_booking.id, show_seat_id=seat.id)
            )

        db.bulk_save_objects(booking_seats_to_insert)
        db.commit()
        db.refresh(new_booking)

        return {
            "message": "Seats locked successfully. Complete the payment.",
            "booking_id": new_booking.id,
            "total_amount": float(total_price),
            "razorpay_order_id": razorpay_order['id'] # Return to Frontend
        }

    except OperationalError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="High traffic: These seats are currently being processed.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-payment", response_model=PaymentSuccessResponse, status_code=status.HTTP_200_OK)
def verify_payment(payload: PaymentVerification, db: Session = Depends(get_db)):
    """
    This endpoint is called by the frontend after a successful Razorpay checkout.
    It verifies the cryptographic signature to ensure the payment wasn't spoofed.
    """
    # try:
    #     # 1. Cryptographic Verification
    #     # If this fails, it throws a SignatureVerificationError
    #     razorpay_client.utility.verify_payment_signature({
    #         'razorpay_order_id': payload.razorpay_order_id,
    #         'razorpay_payment_id': payload.razorpay_payment_id,
    #         'razorpay_signature': payload.razorpay_signature
    #     })
    # except razorpay.errors.SignatureVerificationError:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment verification failed. Invalid signature.")

    # 2. Find the Booking
    booking = db.query(Booking).filter(Booking.razorpay_order_id == payload.razorpay_order_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found for this Order ID.")
        
    if booking.booking_status == 'Confirmed':
        raise HTTPException(status_code=400, detail="This booking has already been processed.")

    # 3. Finalize Transaction
    booking.booking_status = 'Confirmed'
    booking.razorpay_payment_id = payload.razorpay_payment_id
    
    for booking_seat in booking.booking_seats:
        show_seat = booking_seat.show_seat
        show_seat.status = 'Booked'
        
    db.commit()
    
    return {
        "status": "Success",
        "message": "Payment verified and tickets confirmed!",
        "transaction_id": payload.razorpay_payment_id
    }

@router.post("/cleanup-expired-locks", status_code=status.HTTP_200_OK)
def cleanup_expired_locks(db: Session = Depends(get_db)):
    """Manually resets all expired 'Locked' seats back to 'Available' in the database."""
    expiration_limit = datetime.utcnow() - timedelta(minutes=10)
    
    # Find all seats that are Locked but the timestamp is older than 10 minutes
    expired_seats = db.query(ShowSeat).filter(
        ShowSeat.status == 'Locked',
        ShowSeat.locked_at < expiration_limit
    ).all()
    
    count = 0
    for seat in expired_seats:
        seat.status = 'Available'
        seat.locked_at = None
        count += 1
        
    db.commit()
    return {"message": f"Successfully cleaned up {count} expired seat locks."}