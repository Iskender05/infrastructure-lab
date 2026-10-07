import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy import select, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Task
from app.schemas import TaskInput, TaskResponse

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # A bounded retry also supports startup outside Compose or a restarting DB.
    try:
        for attempt in range(1, 31):
            try:
                Base.metadata.create_all(bind=engine)
                break
            except OperationalError:
                if attempt == 30:
                    raise RuntimeError("Database is unavailable after 30 attempts") from None
                logger.warning("Waiting for database (attempt %s/30)", attempt)
                await asyncio.sleep(2)
        yield
    finally:
        engine.dispose()


app = FastAPI(title="Docker Homework: Task API", lifespan=lifespan)
Database = Annotated[Session, Depends(get_db)]


def find_task(task_id: int, db: Session) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/health")
def health(db: Database) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database is unavailable") from None
    return {"status": "ok", "database": "ok"}


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(db: Database):
    return db.scalars(select(Task).order_by(Task.id)).all()


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskInput, db: Database):
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Database):
    return find_task(task_id, db)


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskInput, db: Database):
    task = find_task(task_id, db)
    task.title = payload.title
    task.description = payload.description
    task.completed = payload.completed
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Database) -> Response:
    task = find_task(task_id, db)
    db.delete(task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
