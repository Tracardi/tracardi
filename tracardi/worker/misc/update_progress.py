from celery import Task
from typing import Optional


def update_progress(celery_job: Optional[Task], current: int, total: Optional[int] = 100) -> None:
    """
    Just a simple function not to have to remember the syntax and not to use millions of if statements
    """
    if celery_job:
        celery_job.update_state(state="PROGRESS", meta={"current": current, "total": total})
