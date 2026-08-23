from celery import Celery

celery_app = Celery(
    "youtube_downloader",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    include=["task"]
)

celery_app.conf.update(
    task_track_started = True,
    result_expires=3600,
)