from fastapi import FastAPI
from app.api.v1 import auth, theatres, movies, shows, bookings 
from app.db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="BookMyShow Clone API")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(theatres.router, prefix="/api/v1/theatres", tags=["Theatres"])
app.include_router(movies.router, prefix="/api/v1/movies", tags=["Movies"])
app.include_router(shows.router, prefix="/api/v1/shows", tags=["Shows"])

# 2. MAKE SURE THIS LINE EXISTS
app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["Bookings"]) 

@app.get("/")
def root():
    return {"message": "Welcome to the BookMyShow Clone API"}