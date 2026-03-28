#!/bin/bash
set -e

# Configuration - update these for your setup
PI_HOST="${PI_HOST:-pi@raspberrypi.local}"
PI_PATH="${PI_PATH:-/home/pi/amram-media}"

echo "🚀 Deploying AmramMedia to ${PI_HOST}:${PI_PATH}"

# Sync project files to Pi
rsync -avz --progress \
    --exclude '.git' \
    --exclude '.claude' \
    --exclude 'config/' \
    --exclude '.env' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.venv' \
    ./ "${PI_HOST}:${PI_PATH}/"

echo "📦 Files synced. Building and starting containers..."

# Build and start on the Pi
ssh "${PI_HOST}" "cd ${PI_PATH} && docker compose pull && docker compose up -d --build"

echo "✅ Deployment complete!"
echo ""
echo "Service URLs (replace <pi-ip> with your Pi's IP):"
echo "  Plex:         http://<pi-ip>:32400/web"
echo "  Sonarr:       http://<pi-ip>:8989"
echo "  Radarr:       http://<pi-ip>:7878"
echo "  qBittorrent:  http://<pi-ip>:8080"
echo "  Bazarr:       http://<pi-ip>:6767"
echo "  Prowlarr:     http://<pi-ip>:9696"
