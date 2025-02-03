from celery import Celery
import time
#import redis
import os
from services.update.update_service import UpdateFactory
import asyncio
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

# redis_host = '127.0.0.1'  # Хост Redis-сервера
# redis_port = 6379  # Порт Redis-сервера
# client = redis.Redis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

# if client.ping():
#     print('Успешное подключение к Redis-серверу!')
# else:
#     print('Нет связи с Redis-сервером!')



celery_app = Celery(
'tasks',
broker='redis://redis:6379/0', 
backend='redis://redis:6379/0' 
)

celery_app.autodiscover_tasks()

@celery_app.task
def update_base(date):
    loop = asyncio.get_event_loop()
    updater = UpdateFactory(date)
    return loop.run_until_complete(updater.create_updater())



