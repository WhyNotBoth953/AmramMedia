import os

SONARR_URL = os.environ.get("SONARR_URL", "http://sonarr:8989")
SONARR_API_KEY = os.environ.get("SONARR_API_KEY", "")

RADARR_URL = os.environ.get("RADARR_URL", "http://radarr:7878")
RADARR_API_KEY = os.environ.get("RADARR_API_KEY", "")

QBITTORRENT_URL = os.environ.get("QBITTORRENT_URL", "http://qbittorrent:8080")
QBITTORRENT_USERNAME = os.environ.get("QBITTORRENT_USERNAME", "admin")
QBITTORRENT_PASSWORD = os.environ.get("QBITTORRENT_PASSWORD", "adminadmin")

BAZARR_URL = os.environ.get("BAZARR_URL", "http://bazarr:6767")
BAZARR_API_KEY = os.environ.get("BAZARR_API_KEY", "")

SSD_MOUNT_PATH = "/mnt/ssd"
