# Streaming Server Container

This container packages a complete streaming solution with NGINX-RTMP and HLS support.

## Features
- NGINX with RTMP module for streaming
- Automatic video streaming with FFmpeg
- HLS (HTTP Live Streaming) support
- Web-based video player
- Docker containerization for easy deployment

## Prerequisites
- Docker
- Docker Compose

## Quick Start

1. Clone this repository
2. Place your video files in the `videos` directory
3. Build and run the container:
```bash
docker-compose up --build
```

## Accessing the Stream

- Web Player: http://localhost
- RTMP Stream: rtmp://localhost/live/stream
- HLS Stream: http://localhost/hls/stream.m3u8

## Directory Structure
```
.
├── config/
│   └── nginx.conf
├── videos/
│   └── videoplayback.mp4
├── www/
│   └── public/
│       └── index.html
├── Dockerfile
├── docker-compose.yml
└── docker-entrypoint.sh
```

## Configuration

### Video Source
To use a different video file:
1. Place your video file in the `videos` directory
2. Update the video filename in `docker-entrypoint.sh`

### Stream Settings
FFmpeg streaming parameters can be adjusted in `docker-entrypoint.sh`:
- Video bitrate: `-b:v 3000k`
- Audio bitrate: `-b:a 128k`
- Video preset: `-preset veryfast`

### Custom NGINX Configuration
The NGINX configuration can be modified in `config/nginx.conf`.