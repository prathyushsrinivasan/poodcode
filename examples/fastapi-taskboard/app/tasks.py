from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, Response
from sqlalchemy import select

from .db import Db
from .models import Task
from .schemas import TaskCreate, TaskPatch, TaskRead
from .security import CurrentUser

router = APIRouter(prefix="/tasks", tags=["tasks"])
TaskId = Annotated[int, Path(gt=0)]


def owned_task(task_id: int, db, user_id: int) -> Task:
    task = db.scalar(select(Task).where(Task.id == task_id, Task.owner_id == user_id))
    if task is None:
        raise HTTPException(404, "Task not found")
    return task


@router.post("", response_model=TaskRead, status_code=201)
def create_task(body: TaskCreate, db: Db, user: CurrentUser):
    task = Task(title=body.title, owner_id=user.id)
    db.add(task)
    db.commit()
    return task


@router.get("", response_model=list[TaskRead])
def list_tasks(
    db: Db, user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    done: bool | None = None,
):
    query = select(Task).where(Task.owner_id == user.id)
    if done is not None:
        query = query.where(Task.done == done)
    return db.scalars(query.order_by(Task.id).offset(offset).limit(limit)).all()


@router.get("/{task_id}", response_model=TaskRead)
def read_task(task_id: TaskId, db: Db, user: CurrentUser):
    return owned_task(task_id, db, user.id)


@router.patch("/{task_id}", response_model=TaskRead)
def patch_task(task_id: TaskId, body: TaskPatch, db: Db, user: CurrentUser):
    task = owned_task(task_id, db, user.id)
    for name, value in body.model_dump(exclude_unset=True).items():
        setattr(task, name, value)
    db.commit()
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: TaskId, db: Db, user: CurrentUser):
    task = owned_task(task_id, db, user.id)
    db.delete(task)
    db.commit()
    return Response(status_code=204)
