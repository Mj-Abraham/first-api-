from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="Task API")

# ---------- SQLite Connection ----------

DATABASE = "tasks.db"

conn = sqlite3.connect(DATABASE, check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# ---------- Create Table ----------

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL
)
""")
conn.commit()

# ---------- Insert Sample Tasks ----------

cursor.execute("SELECT COUNT(*) FROM tasks")
count = cursor.fetchone()[0]

if count == 0:
    sample_tasks = [
        ("Complete assignment", 0),
        ("Study FastAPI", 1),
        ("Buy groceries", 0)
    ]

    cursor.executemany(
        "INSERT INTO tasks(title, done) VALUES (?, ?)",
        sample_tasks
    )

    conn.commit()

# ---------- Models ----------

class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str
    done: bool


# ---------- Root ----------

@app.get("/", summary="API Information")
def root():
    return {
        "name": "Task API",
        "version": "2.0",
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

    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"])
        }
        for row in rows
    ]


# ---------- Read One ----------

@app.get("/tasks/{task_id}", summary="Get Task by ID")
def get_task(task_id: int):

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )

    row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail={"error": f"Task {task_id} not found"}
        )

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }


# ---------- Create ----------

@app.post("/tasks",
          status_code=status.HTTP_201_CREATED,
          summary="Create Task")
def create_task(task: TaskCreate):

    if task.title.strip() == "":
        raise HTTPException(
            status_code=400,
            detail={"error": "Title cannot be empty"}
        )

    cursor.execute(
        "INSERT INTO tasks(title, done) VALUES (?, ?)",
        (task.title, 0)
    )

    conn.commit()

    new_id = cursor.lastrowid

    return {
        "id": new_id,
        "title": task.title,
        "done": False
    }


# ---------- Update ----------

@app.put("/tasks/{task_id}", summary="Update Task")
def update_task(task_id: int, updated: TaskUpdate):

    if updated.title.strip() == "":
        raise HTTPException(
            status_code=400,
            detail={"error": "Title cannot be empty"}
        )

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )

    if cursor.fetchone() is None:
        raise HTTPException(
            status_code=404,
            detail={"error": f"Task {task_id} not found"}
        )

    cursor.execute(
        """
        UPDATE tasks
        SET title = ?, done = ?
        WHERE id = ?
        """,
        (
            updated.title,
            int(updated.done),
            task_id
        )
    )

    conn.commit()

    return {
        "id": task_id,
        "title": updated.title,
        "done": updated.done
    }


# ---------- Delete ----------

@app.delete("/tasks/{task_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete Task")
def delete_task(task_id: int):

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )

    if cursor.fetchone() is None:
        raise HTTPException(
            status_code=404,
            detail={"error": f"Task {task_id} not found"}
        )

    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()

    return