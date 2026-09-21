from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql://postgres:Adunni1509$$@localhost:5432/tripeasy"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    #creates a new session to database for every request
    db = SessionLocal()
    try:
        # yield says wait for endpoint to finish using db 
        yield db
    finally:
        db.close()