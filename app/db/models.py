from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Theatre(Base):
    __tablename__ = "theatres"
    id = Column(Integer, primary_key=True, index=True)
    theatre_name = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False)
    location_address = Column(String)

    # Relationships
    users = relationship("User", back_populates="theatre")

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