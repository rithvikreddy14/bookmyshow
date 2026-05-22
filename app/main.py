from fastapi import FastAPI
from app.api.v1 import auth, theatres, movies, shows # Updated imports
from app.db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="BookMyShow Clone API")

# Register the routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(theatres.router, prefix="/api/v1/theatres", tags=["Theatres"])
app.include_router(movies.router, prefix="/api/v1/movies", tags=["Movies"]) # New
app.include_router(shows.router, prefix="/api/v1/shows", tags=["Shows"])    # New

@app.get("/")
def root():
    return {"message": "Welcome to the BookMyShow Clone API"}