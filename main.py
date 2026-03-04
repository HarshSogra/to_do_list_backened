from fastapi import FastAPI, status, HTTPException, Depends,Query
from pydantic import BaseModel
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import models
from datetime import date
from typing import Optional

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Model user sends (NO id)
class TaskCreate(BaseModel):
    title: str
    completed: bool = False
    priority: str | None = None
    deadline: date | None = None


# Model stored internally (WITH id)
class Task(TaskCreate):
    id: int


@app.get("/")
def home():
    return {"message": "Server is working"}


# ✅ Create Task
@app.post("/task")
def add_task(task: TaskCreate, db: Session = Depends(get_db)):

    new_task = models.Task(
        title=task.title,
        completed=task.completed
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


# {✅ Get All Tasks
@app.get("/tasks")
def get_tasks(
        priority: Optional[str] = Query(None),
        sort: Optional[str] = Query(None),
        db: Session = Depends(get_db)
):

        query = db.query(models.Task)
        #filter
        if priority:
            query = query.filter(models.Task.priority == priority)

        #SORT
        if sort == "deadline":
            query = query.order_by(models.Task.deadline)
        tasks = query.all()
        return tasks


# ✅ Get Single Task
@app.get("/task/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):

    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# ✅ Delete Task (ID based)
@app.delete("/task/{task_id}", )
def delete_task(task_id: int, db: Session = Depends(get_db)):

    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}


# ✅ Update Task (ID based)
@app.put("/task/{task_id}", )
def update_task(task_id: int, updated_task: TaskCreate,
                db: Session = Depends(get_db)):

    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.title = updated_task.title
    task.completed = updated_task.completed

    db.commit()
    db.refresh(task)

    return task

#Endpoint
@app.get("/tasks/overdue")
def get_overdue_tasks(db: Session = Depends(get_db)):

    today = date.today()

    overdue_tasks = db.query(models.Task).filter(
        models.Task.deadline < today,
        models.Task.completed == False
    ).all()
    return overdue_tasks

#stats endpoint
@app.get("/tasks/stats")
def task_stats(db: Session = Depends(get_db)):

    total = db.query(models.Task).count()

    completed = db.query(models.Task).filter(
        models.Task.completed == True
    ).count()

    pending = db.query(models.Task).filter(
        models.Task.completed == False
    ).count()

    high_priority = db.query(models.Task).filter(
        models.Task.priority.ilike("high")
    ).count()

    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": pending,
        "high_priority_tasks": high_priority
    }