from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from TodoApp.models import Todo
from TodoApp.database import SessionLocal
from .auth import get_current_user, get_user_from_token
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="TodoApp/templates")

router = APIRouter(
    prefix='/todos',
    tags=['todos']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=302)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response


# ---------------- PAGES ---------------- #

@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    token = request.cookies.get("access_token")
    user = await get_user_from_token(token, db)

    if user is None:
        return redirect_to_login()

    todos = db.query(Todo).filter(Todo.owner_id == user.id).all()
    return templates.TemplateResponse(
        "todo.html",
        {"request": request, "todos": todos, "user": user}
    )


@router.get("/add-todo-page")
async def render_add_todo_page(request: Request, db: db_dependency):
    token = request.cookies.get("access_token")
    user = await get_user_from_token(token, db)

    if user is None:
        return redirect_to_login()

    return templates.TemplateResponse(
        "add-todo.html",
        {"request": request, "user": user}
    )


@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    token = request.cookies.get("access_token")
    user = await get_user_from_token(token, db)

    if user is None:
        return redirect_to_login()

    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.id).first()

    return templates.TemplateResponse(
        "edit-todo.html",
        {"request": request, "todo": todo, "user": user}
    )


# ---------------- API ENDPOINTS ---------------- #

@router.get("/", status_code=200)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    return db.query(Todo).filter(Todo.owner_id == user["id"]).all()


@router.get("/todo/{todo_id}", status_code=200)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = (
        db.query(Todo)
        .filter(Todo.id == todo_id)
        .filter(Todo.owner_id == user["id"])
        .first()
    )

    if todo_model is not None:
        return todo_model

    raise HTTPException(status_code=404, detail="Todo not found.")


@router.post("/todo", status_code=201)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = Todo(
        **todo_request.model_dump(),
        owner_id=user["id"]
    )

    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)

    return todo_model


@router.put("/todo/{todo_id}", status_code=204)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # FIXED filter (owner_id must match user["id"])
    todo_model = (
        db.query(Todo)
        .filter(Todo.id == todo_id)
        .filter(Todo.owner_id == user["id"])
        .first()
    )

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=204)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # FIXED (you used owner_id == todo_id earlier — wrong)
    todo_model = (
        db.query(Todo)
        .filter(Todo.id == todo_id)
        .filter(Todo.owner_id == user["id"])
        .first()
    )

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")

    db.delete(todo_model)
    db.commit()
