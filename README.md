# YTGrab

A FastAPI-based service for downloading YouTube videos asynchronously using Celery and Redis. Submit a video URL, get a task ID back immediately, and poll for progress while the download happens in the background.

## Features

- 🚀 **Async task processing** — downloads run in background workers via Celery, so API requests return instantly
- 📊 **Job status tracking** — poll a task ID to check queued / downloading / completed / failed states
- 🎥 **High-quality downloads** — merges best available video (H.264) and audio streams into MP4 via `yt-dlp` + `ffmpeg`
- 🔒 **URL validation** — restricted to YouTube domains only
- 📁 **File retrieval endpoint** — download the finished file once processing completes

## Tech Stack

- **FastAPI** — REST API layer
- **Celery** — distributed task queue
- **Redis** — message broker and result backend
- **yt-dlp** — video extraction and download engine
- **ffmpeg** — audio/video merging

## Architecture

```
Client → FastAPI → Celery task queue → Redis (broker)
                                            ↓
                                     Celery worker
                                     (yt-dlp + ffmpeg)
                                            ↓
                                     Redis (result backend)
                                            ↓
                              Client polls /download/{task_id}
```

## Prerequisites

- Python 3.9+
- Redis server running locally (or update the broker/backend URLs)
- ffmpeg installed and available on your `PATH`



## Roadmap

- [ ] Rate limiting per client
- [ ] Automatic cleanup of old downloads
- [ ] Docker Compose setup for one-command startup
- [ ] Playlist support

## Disclaimer

This project is intended for educational purposes and personal use with content you have the right to download. Respect YouTube's Terms of Service and applicable copyright laws.
