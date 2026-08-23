import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl

from celery.result import AsyncResult
from celery_app import celery_app
from task import download_video

app = FastAPI()

class videoRequest(BaseModel):
    url: HttpUrl


ALLOWED_HOSTS = {"youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com"}

# def download_video(url: str, output_path="downloads"):
#     os.makedirs(output_path, exist_ok=True)

#     ydl_opts = {
#         "format": "bestvideo[vcodec^=avc1]+bestaudio[acodec^=mp4a]/best[ext=mp4]",
#         "merge_output_format": "mp4",
#         "outtmpl": f"{output_path}/%(title)s.%(ext)s",
#     }

#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#                 info = ydl.extract_info(str(url), download=True)
#                 return{
#                     "title": info["title"],
#                     "duration": info.get("duration"),
#                 }
#     except DownloadError as e:
#          raise HTTPException(
#               status_code=400,
#               detail=f"Failed to download video Unsupported URL:{url}",
#          ) 


@app.get("/")
def home():
    return {"message": "YouTube Downloader API"}

@app.post("/download")
def create_download(payload: videoRequest):
    if payload.url.host not in ALLOWED_HOSTS:
        raise HTTPException(status_code=400, detail="Only YouTube URLs are supported")

    task = download_video.delay(str(payload.url))
    return {
        "task_id": task.id,
        "status": "queued"
    }


@app.get("/download/{task_id}")
def get_download_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)

    if task.state == "PENDING":
        return {"task_id": task_id, "status": "queued"}

    if task.state == "STARTED":
        return {"task_id": task_id, "status": "downloading"}

    if task.state == "SUCCESS":
        return {"task_id": task_id, "status": "completed", "result": task.result}

    if task.state == "FAILURE":
        return {"task_id": task_id, "status": "failed", "error": str(task.result)}

    return {"task_id": task_id, "status": task.state}


@app.get("/download/{task_id}/file")
def get_file(task_id: str):
    task = AsyncResult(task_id, app=celery_app)

    if task.state != "SUCCESS":
        raise HTTPException(status_code=400, detail="File not ready")

    filepath = task.result.get("filepath")
    if not filepath or not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(filepath, filename=os.path.basename(filepath))