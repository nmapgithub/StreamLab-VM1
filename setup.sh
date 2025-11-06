#!/bin/bash

# Install required packages
apt-get update
apt-get install -y \
    nginx \
    nginx-module-rtmp \
    ffmpeg \
    nodejs \
    npm \
    sqlite3 \
    build-essential

# Create necessary directories
mkdir -p /tmp/hls
mkdir -p /tmp/recordings
mkdir -p /var/www/streamlab
mkdir -p /var/log/streamlab

# Set up the database with vulnerable data
cat << EOF | sqlite3 /var/www/streamlab/streams.db
CREATE TABLE streams (
    id INTEGER PRIMARY KEY,
    key TEXT,
    metadata TEXT
);

-- Insert vulnerable stream data with part 2 of the flag
INSERT INTO streams (key, metadata) VALUES (
    'default_stream_key',
    '{"title": "Test Stream", "flag": "STREAM_FLAG{p4rt_2_0f_4}"}'
);
EOF

# Set up vulnerable RTMP module
cat << EOF > /usr/local/nginx/conf/rtmp.conf
load_module modules/ngx_rtmp_module.so;
EOF

# Create vulnerable stream token with part 3 of flag
echo "STREAM_FLAG{p4rt_3_0f_4}" > /var/www/streamlab/token.key

# Set up FFmpeg preprocessing script with part 4 of flag embedded in metadata
cat << EOF > /var/www/streamlab/preprocess.sh
#!/bin/bash
ffmpeg -i "\$1" -metadata flag="STREAM_FLAG{p4rt_4_0f_4}" -c copy "\$2"
EOF
chmod +x /var/www/streamlab/preprocess.sh

# Install Node.js dependencies
cd /var/www/streamlab
npm install express sqlite3 crypto-js ws

# Set up systemd service
cat << EOF > /etc/systemd/system/streamlab.service
[Unit]
Description=StreamLab CTF Challenge
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/streamlab
ExecStart=/usr/bin/node server.js
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start services
systemctl daemon-reload
systemctl enable streamlab
systemctl start streamlab
systemctl restart nginx

# Set up iptables rules to only allow necessary ports
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 1935 -j ACCEPT
iptables -A INPUT -p tcp --dport 8080 -j ACCEPT

echo "StreamLab CTF challenge setup complete!"