import time

from celery import Celery

from tracardi.config import redis_config

celery = Celery(
    __name__,
    broker=redis_config.get_redis_with_password(),
    backend=redis_config.get_redis_with_password()
)


@celery.task(bind=True)
def run_celery_replay_job(self):
    for x in range(0, 100):
        self.update_state(state="PROGRESS", meta={'current': x, 'total': 100})
        time.sleep(.5)
