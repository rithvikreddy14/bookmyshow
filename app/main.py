from fastapi import FastAPI
from app.api.v1 import auth
from app.db.database import engine, Base

# This line automatically creates the tables in Neon if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="BookMyShow Clone API")

# Register the Auth routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

@app.get("/")
def root():
    return {"message": "Welcome to the BookMyShow Clone API"}