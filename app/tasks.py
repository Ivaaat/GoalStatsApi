from celery import Celery
from services.update.update_service import UpdateFacade
import asyncio
from celery.schedules import crontab
from datetime import datetime



celery_app = Celery(
'tasks',
broker='redis://redis:6379/0', 
backend='redis://redis:6379/0' 
)


# celery_app.conf.beat_schedule = {
#     'update-base-every-minute': {
#         'task': 'tasks.update_base',
#         'schedule': crontab(minute='*/1'),
#         'args': (datetime.now().strftime('%Y-%m-%d'),),
#     },
# }

@celery_app.task
def update_base(date):
    loop = asyncio.get_event_loop()
    updater = UpdateFacade(date)
    return loop.run_until_complete(updater.run())



