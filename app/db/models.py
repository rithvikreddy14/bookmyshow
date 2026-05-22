from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Date, DateTime, Numeric
from sqlalchemy.orm import relationship
from app.db.database import Base
from sqlalchemy.sql import func

class Theatre(Base):
    __tablename__ = "theatres"
    id = Column(Integer, primary_key=True, index=True)
    theatre_name = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False)
    location_address = Column(String)

    # Relationships
    users = relationship("User", back_populates="theatre")
    screens = relationship("Screen", back_populates="theatre", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(15))
    role = Column(Enum('SuperAdmin', 'TheatreAdmin', 'Customer', 'Staff', name="user_roles"), default='Customer')
    
    # Foreign Keys
    theatre_id = Column(Integer, ForeignKey("theatres.id"), nullable=True)

    # Relationships
    theatre = relationship("Theatre", back_populates="users")

class Screen(Base):
    __tablename__ = "screens"
    id = Column(Integer, primary_key=True, index=True)
    theatre_id = Column(Integer, ForeignKey("theatres.id", ondelete="CASCADE"), nullable=False)
    screen_name = Column(String(50), nullable=False)
    total_capacity = Column(Integer, nullable=False)

    # Relationships
    theatre = relationship("Theatre", back_populates="screens")
    seats = relationship("Seat", back_populates="screen", cascade="all, delete-orphan")

class Seat(Base):
    __tablename__ = "seats"
    id = Column(Integer, primary_key=True, index=True)
    screen_id = Column(Integer, ForeignKey("screens.id", ondelete="CASCADE"), nullable=False)
    row_identifier = Column(String(5), nullable=False)
    seat_number = Column(Integer, nullable=False)
    seat_type = Column(Enum('Standard', 'Premium', 'Recliner', name="seat_types"), default='Standard')

    # Relationships
    screen = relationship("Screen", back_populates="seats")

class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    language = Column(String(50))
    genre = Column(String(50))
    duration_mins = Column(Integer)
    release_date = Column(Date)

    # Relationships
    shows = relationship("Show", back_populates="movie", cascade="all, delete-orphan")

class Show(Base):
    __tablename__ = "shows"
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    screen_id = Column(Integer, ForeignKey("screens.id", ondelete="CASCADE"), nullable=False)
    show_date = Column(Date, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    # Relationships
    movie = relationship("Movie", back_populates="shows")
    screen = relationship("Screen", backref="shows")

class ShowSeat(Base):
    __tablename__ = "show_seats"
    id = Column(Integer, primary_key=True, index=True)
    show_id = Column(Integer, ForeignKey("shows.id", ondelete="CASCADE"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.id", ondelete="CASCADE"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum('Available', 'Locked', 'Booked', name="seat_status"), default='Available')
    locked_at = Column(DateTime, nullable=True)

    # Relationships
    show = relationship("Show", backref="show_seats")
    seat = relationship("Seat", backref="show_mappings")


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    show_id = Column(Integer, ForeignKey("shows.id", ondelete="CASCADE"), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    booking_status = Column(Enum('Pending', 'Confirmed', 'Cancelled', name="booking_status_enum"), default='Pending')
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", backref="bookings")
    show = relationship("Show", backref="bookings")
    booking_seats = relationship("BookingSeat", back_populates="booking", cascade="all, delete-orphan")

class BookingSeat(Base):
    __tablename__ = "booking_seats"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    show_seat_id = Column(Integer, ForeignKey("show_seats.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    booking = relationship("Booking", back_populates="booking_seats")
    show_seat = relationship("ShowSeat", backref="booking_links")