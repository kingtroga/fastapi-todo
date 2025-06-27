import os
from sqlalchemy import create_engine, Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

# For Vercel serverless - use in-memory SQLite database
# This will reset on each function invocation but won't crash
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create engine with proper settings for serverless
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30
    },
    pool_pre_ping=True,
    echo=False  # Set to True for debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TodoDB(Base):
    __tablename__ = "todos"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

# Global variable to ensure tables are created only once per function instance
_tables_created = False

def create_tables():
    global _tables_created
    if not _tables_created:
        Base.metadata.create_all(bind=engine)
        _tables_created = True
        
        # Add some sample data for demonstration
        db = SessionLocal()
        try:
            # Check if we already have data
            existing_todos = db.query(TodoDB).first()
            if not existing_todos:
                sample_todos = [
                    TodoDB(title="Learn FastAPI", description="Build a todo API with FastAPI", completed=True),
                    TodoDB(title="Deploy to Vercel", description="Deploy the FastAPI app to Vercel", completed=True),
                    TodoDB(title="Add frontend", description="Create a React frontend for the todo app", completed=False),
                    TodoDB(title="Add authentication", description="Implement user authentication", completed=False),
                ]
                for todo in sample_todos:
                    db.add(todo)
                db.commit()
        except Exception as e:
            print(f"Error adding sample data: {e}")
            db.rollback()
        finally:
            db.close()

def get_db():
    # Ensure tables are created
    create_tables()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()