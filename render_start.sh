#!/bin/bash
cd /opt/render/project/src/backend
exec gunicorn backend.asgi:application -k uvicorn.workers.UvicornWorker -w 4 --bind 0.0.0.0:$PORT
