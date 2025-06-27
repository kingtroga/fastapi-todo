from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db, TodoDB
from exceptions import TodoNotFoundError, todo_not_found_handler

app = FastAPI(title="Todo API", version="1.0.0")
app.add_exception_handler(TodoNotFoundError, todo_not_found_handler)


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

@app.get("/")
async def root():
    return {"message": "Welcome to the Todo API"}

@app.post("/todos/", response_model=Todo)
async def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = TodoDB(
        title=todo.title,
        description=todo.description
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos/", response_model=List[Todo])
async def get_todos(
    completed: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
    ):
    query = db.query(TodoDB)

    if completed is not None:
        query = query.filter(TodoDB.completed == completed)

    if search:
        query = query.filter(TodoDB.title.contains(search))

    return query.all()

@app.patch("/todos/{todo_id}/toggle", response_model=Todo)
async def toggle_todo(todo_id: str, db: Session = Depends(get_db)):
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo.completed = not todo.completed
    db.commit()
    db.refresh(todo)
    return todo

@app.get("/todo/{todo_id}", response_model=Todo)
async def get_todo(todo_id: str, db: Session = Depends(get_db)):
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: str, todo_update: TodoUpdate, db: Session = Depends(get_db)):
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
 

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: str, db: Session = Depends(get_db)):
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if not todo:
        return HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)