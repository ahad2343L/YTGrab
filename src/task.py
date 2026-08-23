import os
import uuid

import yt_dlp

from yt_dlp.utils import DownloadError
from celery_app import celery_app


@celery_app.task(bind=True)
def download_video(self, url: str):
    job_id = uuid.uuid4().hex[:8]
    output_dir = os.path.join("downloads", job_id)
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestvideo[vcodec^=avc1]+bestaudio/best",
        "outtmpl": output_path,
        "merge_output_format": "mp4",
        "restrictfilenames": True,   # avoids weird/unsafe chars in filenames
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)

            if ydl_opts.get("merge_output_format"):
                base, _ = os.path.splitext(filepath)
                filepath = f"{base}.{ydl_opts['merge_output_format']}"
    except DownloadError as e:
        raise RuntimeError(f"Failed to download: {e}") from e

    return {
        "title": info.get("title"),
        "duration": info.get("duration"),
        "filepath": filepath,
        "status": "completed",
    }