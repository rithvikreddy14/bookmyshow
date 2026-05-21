from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Create the database engine
# Neon requires secure connections, which is handled natively by the driver if ?sslmode=require is in the URL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True, # Verifies connection is alive before routing a request
    pool_size=10,       # Base number of connections to keep open
    max_overflow=20     # Max additional connections during traffic spikes
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get the DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()