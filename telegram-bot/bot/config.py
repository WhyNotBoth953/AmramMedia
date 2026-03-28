import os
import sys

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_ALLOWED_CHAT_IDS = {
    int(cid.strip())
    for cid in os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS", "").split(",")
    if cid.strip()
}

SONARR_URL = os.environ.get("SONARR_URL", "http://sonarr:8989")
SONARR_API_KEY = os.environ.get("SONARR_API_KEY", "")

RADARR_URL = os.environ.get("RADARR_URL", "http://radarr:7878")
RADARR_API_KEY = os.environ.get("RADARR_API_KEY", "")

QBITTORRENT_URL = os.environ.get("QBITTORRENT_URL", "http://qbittorrent:8080")
QBITTORRENT_USERNAME = os.environ.get("QBITTORRENT_USERNAME", "admin")
QBITTORRENT_PASSWORD = os.environ.get("QBITTORRENT_PASSWORD", "adminadmin")

PLEX_URL = os.environ.get("PLEX_URL", "http://plex:32400")
PLEX_TOKEN = os.environ.get("PLEX_TOKEN", "")

POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "30"))

# Paths inside the container
SSD_MOUNT_PATH = "/mnt/ssd"

if not TELEGRAM_BOT_TOKEN:
    print("ERROR: TELEGRAM_BOT_TOKEN is required", file=sys.stderr)
    sys.exit(1)
