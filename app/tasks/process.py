from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

@celery_app.task
def process_statistics(link_id: int):
    # Пример фоновой задачи для обработки статистики.
    # Здесь можно, например, агрегировать данные или отправлять уведомления.
    print(f"Processing statistics for link {link_id}")