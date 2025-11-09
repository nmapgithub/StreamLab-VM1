# Use Ubuntu as base image
FROM ubuntu:22.04

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && apt-get install -y \
    nginx \
    libnginx-mod-rtmp \
    ffmpeg \
    gettext-base \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create directories for HLS and recordings
RUN mkdir -p /tmp/hls /tmp/recordings \
    && chown -R www-data:www-data /tmp/hls /tmp/recordings \
    && chmod -R 755 /tmp/hls /tmp/recordings

# Copy NGINX configuration
COPY config/nginx.conf /etc/nginx/nginx.conf

# Copy web files
COPY www/public /var/www/stream

# Copy video files
COPY videos /opt/videos

# Set proper permissions
RUN chown -R www-data:www-data /var/www/stream \
    && chmod -R 755 /var/www/stream

# Create directories for NGINX pid and SSL certificates
RUN mkdir -p /run/nginx /etc/nginx/ssl


# Expose ports
EXPOSE 80
EXPOSE 443
EXPOSE 1935


# Copy entrypoint, broadcast, and video switcher scripts
COPY docker-entrypoint.sh /
COPY broadcast.sh /
COPY video-switcher.sh /
RUN sed -i 's/\r$//' /docker-entrypoint.sh /broadcast.sh /video-switcher.sh && \
    chmod +x /docker-entrypoint.sh /broadcast.sh /video-switcher.sh

# Set entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]