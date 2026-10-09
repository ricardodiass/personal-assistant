from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import TaskModel


router = APIRouter(prefix="/tasks", tags=["Tasks"])


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    completed: bool = False


@router.post("/", response_model=Task, status_code=201)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
) -> TaskModel:
    task = TaskModel(
        id=str(uuid4()),
        title=task_data.title,
        description=task_data.description,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@router.get("/", response_model=list[Task])
def list_tasks(db: Session = Depends(get_db)) -> list[TaskModel]:
    result = db.scalars(select(TaskModel).order_by(TaskModel.title))
    return list(result.all())


@router.patch("/{task_id}/complete", response_model=Task)
def complete_task(
    task_id: str,
    db: Session = Depends(get_db),
) -> TaskModel:
    task = db.get(TaskModel, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = True
    db.commit()
    db.refresh(task)

    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
) -> None:
    task = db.get(TaskModel, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
