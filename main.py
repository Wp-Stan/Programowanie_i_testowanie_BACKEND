from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr
from typing import Optional, List
from datetime import datetime, timezone
import json
import os
import threading

app = FastAPI()

TASKS_FILE = "tasks.json"
lock = threading.Lock()  # zabezpieczenie, żeby zapis nie mieszał się przy wielu requestach


# ---------- MODELE DANYCH ----------

# Limity (możesz zmienić jak chcesz):
# - title: 1–50 znaków, wymagany
# - description: maks 200 znaków, opcjonalny

class TaskCreate(BaseModel):
    title: constr(min_length=1, max_length=50)
    description: Optional[constr(max_length=200)] = None


class TaskUpdate(BaseModel):
    title: Optional[constr(min_length=1, max_length=50)] = None
    description: Optional[constr(max_length=200)] = None
    completed: Optional[bool] = None


# ---------- FUNKCJE POMOCNICZE ----------

def get_timestamp() -> str:
    """Zwraca timestamp w stylu 2024-11-15T10:30:00Z."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_tasks() -> List[dict]:
    """Czyta listę tasków z pliku JSON."""
    if not os.path.exists(TASKS_FILE):
        return []

    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except json.JSONDecodeError:
        # plik uszkodzony – realnie można rzucić 500, ale dla prostoty: pusto
        return []


def write_tasks(tasks: List[dict]) -> None:
    """Zapisuje listę tasków do pliku JSON."""
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def get_next_id(tasks: List[dict]) -> int:
    """Generuje kolejny ID."""
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1


# ---------- ENDPOINTY ----------

@app.get("/health")
def get_health():
    return {
        "status": "OK",
        "timestamp": get_timestamp(),
    }


@app.get("/tasks")
def get_tasks():
    tasks = read_tasks()
    return tasks


@app.post("/tasks", status_code=201)
def create_task(task_data: TaskCreate):
    # TaskCreate już tutaj waliduje długość title/description
    with lock:
        tasks = read_tasks()
        new_id = get_next_id(tasks)
        now = get_timestamp()

        task = {
            "id": new_id,
            "title": task_data.title,
            "description": task_data.description,
            "completed": False,
            "createdAt": now,
        }

        tasks.append(task)
        write_tasks(tasks)

    return task

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    tasks = read_tasks()
    for task in tasks:
        if task["id"] == task_id:
            return task

    return JSONResponse(
        status_code=404,
        content={"error": "Task not found", "id": task_id},
    )

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    with lock:
        tasks = read_tasks()
        new_tasks = [task for task in tasks if task["id"] != task_id]

        if len(new_tasks) == len(tasks):
            return JSONResponse(
                status_code=404,
                content={"error": "Task not found", "id": task_id},
            )

        write_tasks(new_tasks)

    return {"status": "deleted", "id": task_id}


@app.put("/tasks/{task_id}")
def update_task(task_id: int, update_data: TaskUpdate):
    # TaskUpdate też ma walidację długości
    with lock:
        tasks = read_tasks()

        for task in tasks:
            if task["id"] == task_id:

                if update_data.title is not None:
                    task["title"] = update_data.title
                if update_data.description is not None:
                    task["description"] = update_data.description
                if update_data.completed is not None:
                    task["completed"] = update_data.completed

                task["updatedAt"] = get_timestamp()

                write_tasks(tasks)
                return task

    return JSONResponse(
        status_code=404,
        content={"error": "Task not found", "id": task_id},
    )


# Globalny handler błędów (żeby testy ładnie dostawały 500 zamiast krzaka)
@app.exception_handler(Exception)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error"},
    )
