from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # Add this import
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.schemas.user_schema import UserCreate, UserResponse, Token # Removed UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    new_user = User(
        name=user.name, 
        email=user.email, 
        password_hash=hashed_password, 
        phone=user.phone,
        role="Customer" # Default role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- UPDATED LOGIN ROUTE ---
@router.post("/login", response_model=Token)
def login_user(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2 strongly enforces the field name 'username', so we check our 'email' column against it
    user = db.query(User).filter(User.email == user_credentials.username).first()
    
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )
    
    # Generate JWT
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}