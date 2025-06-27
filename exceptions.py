from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

class TodoNotFoundError(Exception):
    def __init__(self, todo_id: str):
        self.todo_id = todo_id

async def todo_not_found_handler(request: Request, exc: TodoNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Todo with id {exc.todo_id} not found"}
    )