#!/bin/bash

# Video Switcher Script for Dynamic Stream Control
# This script monitors /tmp/current_video.txt and restarts FFmpeg when video changes

CURRENT_VIDEO="/opt/videos/videoplayback.mp4"
VIDEO_FILE="/tmp/control/current_video.txt"
FFMPEG_PID=""

# Create control directory
mkdir -p /tmp/control

echo "[Video Switcher] Starting video switcher daemon..."

# Function to start FFmpeg stream
start_stream() {
    local video=$1
    echo "[Video Switcher] Starting stream with: $video"
    
    # Kill existing FFmpeg process if running
    if [ ! -z "$FFMPEG_PID" ] && kill -0 $FFMPEG_PID 2>/dev/null; then
        echo "[Video Switcher] Stopping existing stream (PID: $FFMPEG_PID)"
        kill $FFMPEG_PID
        wait $FFMPEG_PID 2>/dev/null
    fi
    
    # Start new FFmpeg stream
    ffmpeg -re -stream_loop -1 -i "$video" \
        -c:v libx264 -preset veryfast -b:v 3000k -maxrate 3000k -bufsize 6000k \
        -pix_fmt yuv420p -g 50 -c:a aac -b:a 128k -ac 2 -ar 44100 \
        -f flv rtmp://localhost/live/stream &
    
    FFMPEG_PID=$!
    echo "[Video Switcher] Stream started (PID: $FFMPEG_PID)"
}

# Initialize with default video
echo "[Video Switcher] Initializing with default video: $CURRENT_VIDEO"
start_stream "$CURRENT_VIDEO"

# Monitor for video changes
echo "[Video Switcher] Monitoring for video changes..."
while true; do
    if [ -f "$VIDEO_FILE" ]; then
        NEW_VIDEO=$(cat "$VIDEO_FILE")
        
        # Check if video has changed
        if [ "$NEW_VIDEO" != "$(basename $CURRENT_VIDEO)" ]; then
            FULL_PATH="/opt/videos/$NEW_VIDEO"
            
            if [ -f "$FULL_PATH" ]; then
                echo "[Video Switcher] ⚠️  VIDEO HIJACKED! Switching to: $NEW_VIDEO"
                CURRENT_VIDEO="$FULL_PATH"
                start_stream "$CURRENT_VIDEO"
                
                # Log the hack attempt
                echo "$(date): Stream hijacked - switched to $NEW_VIDEO" >> /tmp/control/hijack_log.txt
            else
                echo "[Video Switcher] ❌ Video not found: $FULL_PATH"
            fi
        fi
    fi
    
    # Check if FFmpeg is still running, restart if crashed
    if ! kill -0 $FFMPEG_PID 2>/dev/null; then
        echo "[Video Switcher] ⚠️  FFmpeg crashed! Restarting..."
        start_stream "$CURRENT_VIDEO"
    fi
    
    sleep 3
done

