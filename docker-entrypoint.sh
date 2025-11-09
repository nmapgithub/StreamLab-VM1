#!/bin/bash

set -e

echo "========================================"
echo "  ANN News - Live Streaming Server"
echo "  Penetration Testing Lab Environment"
echo "========================================"

# Start NGINX
echo "[NGINX] Starting web server..."
nginx

# Wait for NGINX to start
sleep 2

echo "[NGINX] Web server started"

# Initialize video switcher control file
echo "[VIDEO] Initializing video control system..."
mkdir -p /tmp/control
echo "videoplayback.mp4" > /tmp/control/current_video.txt
echo "[VIDEO] Control system ready"

# Start video switcher daemon in background
echo "[VIDEO] Starting dynamic video switcher..."
/video-switcher.sh &

echo ""
echo "========================================"
echo "  System Ready!"
echo "========================================"
echo "  Web Player:  https://ann-news.live"
echo "  Management:  https://manage.ann-news.live"
echo "  RTMP Stream: rtmp://localhost:1935/live/stream"
echo "========================================"
echo ""
echo "WARNING: PENTESTING LAB - Vulnerabilities Present!"
echo "  Check /PENTESTING-LAB-GUIDE.md for details"
echo ""

# Keep container running and show logs
tail -f /var/log/nginx/error.log
