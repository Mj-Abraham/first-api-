from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="Task API")


# ---------- Models ----------

class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str
    done: bool


# ---------- In-memory Tasks ----------

tasks = [
    {"id": 1, "title": "Complete assignment", "done": False},
    {"id": 2, "title": "Study FastAPI", "done": True},
    {"id": 3, "title": "Buy groceries", "done": False}
]


# ---------- Root ----------

@app.get("/", summary="API Information")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


# ---------- Health ----------

@app.get("/health", summary="Health Check")
def health():
    return {
        "status": "ok"
    }


# ---------- Read All ----------

@app.get("/tasks", summary="Get All Tasks")
def get_tasks():
    return tasks


# ---------- Read One ----------

@app.get("/tasks/{task_id}", summary="Get Task by ID")
def get_task(task_id: int):

    for task in tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=404,
        detail={"error": f"Task {task_id} not found"}
    )


# ---------- Create ----------

@app.post("/tasks", status_code=status.HTTP_201_CREATED,
          summary="Create Task")
def create_task(task: TaskCreate):

    if task.title.strip() == "":
        raise HTTPException(
            status_code=400,
            detail={"error": "Title cannot be empty"}
        )

    new_task = {
        "id": len(tasks) + 1,
        "title": task.title,
        "done": False
    }

    tasks.append(new_task)

    return new_task


# ---------- Update ----------

@app.put("/tasks/{task_id}", summary="Update Task")
def update_task(task_id: int, updated: TaskUpdate):

    if updated.title.strip() == "":
        raise HTTPException(
            status_code=400,
            detail={"error": "Title cannot be empty"}
        )

    for task in tasks:

        if task["id"] == task_id:

            task["title"] = updated.title
            task["done"] = updated.done

            return task

    raise HTTPException(
        status_code=404,
        detail={"error": f"Task {task_id} not found"}
    )


# ---------- Delete ----------

@app.delete("/tasks/{task_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete Task")
def delete_task(task_id: int):

    for task in tasks:

        if task["id"] == task_id:

            tasks.remove(task)

            return

    raise HTTPException(
        status_code=404,
        detail={"error": f"Task {task_id} not found"}
    )