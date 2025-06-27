from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db, TodoDB

app = FastAPI(
    title="Todo API",
    version="1.0.0",
    description="A simple Todo API built with FastAPI and deployed on Vercel. Made with love by https://www.instagram.com/atari.can/"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class Todo(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True

@app.get("/")
def root():
    return {
        "message": "Welcome to the Todo API! 🚀", 
        "docs": "/docs",
        "status": "running on Vercel",
        "endpoints": {
            "get_todos": "GET /todos/",
            "create_todo": "POST /todos/",
            "get_todo": "GET /todos/{todo_id}",
            "update_todo": "PUT /todos/{todo_id}",
            "delete_todo": "DELETE /todos/{todo_id}",
            "toggle_todo": "PATCH /todos/{todo_id}/toggle"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/test")
def test():
    return {
        "message": "Test endpoint working",
        "framework": "FastAPI",
        "platform": "Vercel"
    }

@app.post("/todos/", response_model=Todo)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    """Create a new todo item"""
    try:
        db_todo = TodoDB(
            title=todo.title,
            description=todo.description
        )
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating todo: {str(e)}")

@app.get("/todos/", response_model=List[Todo])
def get_todos(
    completed: Optional[bool] = None,
    search: Optional[str] = None,
    limit: Optional[int] = 100,
    db: Session = Depends(get_db)
):
    """Get all todos with optional filtering"""
    try:
        query = db.query(TodoDB)
        
        if completed is not None:
            query = query.filter(TodoDB.completed == completed)
        
        if search:
            query = query.filter(TodoDB.title.contains(search))
        
        query = query.limit(limit)
        return query.all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching todos: {str(e)}")

@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: str, db: Session = Depends(get_db)):
    """Get a specific todo by ID"""
    try:
        todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        return todo
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching todo: {str(e)}")

@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: str, todo_update: TodoUpdate, db: Session = Depends(get_db)):
    """Update a todo item"""
    try:
        todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        if todo_update.title is not None:
            todo.title = todo_update.title
        if todo_update.description is not None:
            todo.description = todo_update.description
        if todo_update.completed is not None:
            todo.completed = todo_update.completed
        
        db.commit()
        db.refresh(todo)
        return todo
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating todo: {str(e)}")

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: str, db: Session = Depends(get_db)):
    """Delete a todo item"""
    try:
        todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        db.delete(todo)
        db.commit()
        return {"message": "Todo deleted successfully", "deleted_id": todo_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting todo: {str(e)}")

@app.patch("/todos/{todo_id}/toggle", response_model=Todo)
def toggle_todo(todo_id: str, db: Session = Depends(get_db)):
    """Toggle the completed status of a todo"""
    try:
        todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        todo.completed = not todo.completed
        db.commit()
        db.refresh(todo)
        return todo
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error toggling todo: {str(e)}")