# AmramMedia

A self-hosted media management system for Raspberry Pi 4, controlled through a Telegram bot and a web dashboard. Automates downloading, organizing, and monitoring movies and TV series with Hebrew subtitle support.

## Features

- **Telegram Bot** - Full control from your phone: search, download, monitor, manage
- **Web Dashboard** - Mobile-friendly dark UI for browsing library, monitoring downloads, and managing content
- **Hebrew Subtitles** - Automatic subtitle downloads via Bazarr (Ktuvit, OpenSubtitles)
- **Download Notifications** - Get notified on Telegram when downloads complete
- **Service Control** - Restart Docker services remotely via Telegram

## Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/search <title>` | Search movies and series |
| `/movie <title>` | Search and add a movie |
| `/series <title>` | Search and add a TV series |
| `/delete <title>` | Remove content from library |
| `/status` | View active downloads |
| `/library` | Library statistics |
| `/upcoming` | Upcoming episodes (7 days) |
| `/disk` | Disk space info |
| `/restart <service>` | Restart a service |

## Web Dashboard

Accessible at `http://<pi-ip>:8000` with 5 tabs:

- **Dashboard** - Library stats, disk usage, upcoming episodes, missing subtitles
- **Movies** - Poster grid with filter, file status badges, delete
- **Series** - Poster grid with episode progress, seasons count
- **Downloads** - Live progress bars (auto-refreshes every 5s)
- **Search** - Search and add movies/series with one click

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Bot | Python 3.11, python-telegram-bot 21.3, aiohttp |
| Dashboard | FastAPI, vanilla HTML/CSS/JS (no build step) |
| Media | Plex, Sonarr, Radarr, Bazarr, Prowlarr |
| Downloads | qBittorrent |
| Deployment | Docker Compose on Raspberry Pi 4 (arm64) |

## Services

| Service | Port | Description |
|---------|------|-------------|
| Plex | 32400 | Media streaming (Direct Play only) |
| Sonarr | 8989 | TV series management |
| Radarr | 7878 | Movie management |
| qBittorrent | 8080 | Torrent client |
| Bazarr | 6767 | Subtitle management |
| Prowlarr | 9696 | Indexer proxy |
| Web Dashboard | 8000 | Media management UI |

## Setup

1. Copy `.env.example` to `.env` on your Pi and fill in credentials:
   - Telegram bot token (from @BotFather)
   - Allowed chat IDs (from @userinfobot)
   - Plex claim token (from https://plex.tv/claim)
   - API keys are collected after first startup from each service's Settings page

2. Prepare the Pi:
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker pi

   # Create download directories
   mkdir -p /mnt/ssd/Downloads/{complete,incomplete}

   # Create config directories
   mkdir -p /home/pi/amram-media/config/{plex,sonarr,radarr,qbittorrent,bazarr,prowlarr}
   ```

3. Deploy:
   ```bash
   PI_HOST=pi@<your-pi-ip> ./deploy.sh
   ```

4. Configure services via their web UIs, collect API keys, update `.env`, then:
   ```bash
   docker compose restart telegram-bot web-dashboard
   ```

## Architecture

All services run as Docker containers on a shared bridge network (`media-net`), except Plex which uses host networking for device discovery. Total memory usage ~3GB, fitting within the Pi 4's 4GB RAM.

```
Telegram / Web UI
       |
  Telegram Bot / FastAPI Dashboard
       |
  Sonarr / Radarr --> Prowlarr (indexers)
       |
  qBittorrent (downloads to /mnt/ssd/Downloads)
       |
  Sonarr/Radarr (moves to /mnt/ssd/Movies or /mnt/ssd/Series)
       |
  Bazarr (downloads Hebrew subtitles)
       |
  Plex (serves to clients)
```
