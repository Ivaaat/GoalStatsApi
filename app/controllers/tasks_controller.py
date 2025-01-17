from fastapi import APIRouter
from tasks import update_base

router = APIRouter()

@router.post("/update/")
async def run_task(date: str):
    task = update_base.delay(date) 
    return {"task_id": task.id}


@router.get("/update/{task_id}")
async def get_task_status(task_id: str):
    task_result = update_base.AsyncResult(task_id)
    return {
    "task_id": task_result.id,
    "status": task_result.status,
    "result": task_result.result if task_result.ready() else None,
    }