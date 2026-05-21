from fastapi import FastAPI
from app.api.v1 import auth, theatres
from app.db.database import engine, Base

# This line automatically creates the tables in Neon if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="BookMyShow Clone API")

# Register the routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(theatres.router, prefix="/api/v1/theatres", tags=["Theatres"])

@app.get("/")
def root():
    return {"message": "Welcome to the BookMyShow Clone API"}