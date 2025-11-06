#!/bin/bash

VIDEO_PATH="$1"
STREAM_URL="rtmp://localhost/live/stream"

if [ -z "$VIDEO_PATH" ]; then
    echo "Usage: $0 <path-to-video-file>"
    exit 1
fi

if [ ! -f "$VIDEO_PATH" ]; then
    echo "Error: Video file not found!"
    exit 1
fi

echo "Starting continuous broadcast of: $VIDEO_PATH"
echo "Streaming to: $STREAM_URL"

while true; do
    ffmpeg -re -i "$VIDEO_PATH" \
        -c:v libx264 -preset veryfast -b:v 3000k \
        -c:a aac -b:a 128k \
        -f flv "$STREAM_URL"
    
    echo "Stream ended, restarting in 2 seconds..."
    sleep 2
done