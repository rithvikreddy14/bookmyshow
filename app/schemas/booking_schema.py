from pydantic import BaseModel
from typing import List, Optional

class BookingCreate(BaseModel):
    show_id: int
    seat_ids: List[int]

class BookingResponse(BaseModel):
    booking_id: int
    total_amount: float
    message: str
    razorpay_order_id: str # The frontend needs this to open the payment popup


class PaymentVerification(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class PaymentSuccessResponse(BaseModel):
    status: str
    message: str
    transaction_id: str