# AmramMedia Project

## Overview
Docker Compose media stack with Telegram bot control and web dashboard.
Deployed on a home server (i7-12700H, 16GB RAM, Ubuntu) at 192.168.0.148.

## Architecture
```
Prowlarr (indexers) → Sonarr/Radarr (management) → qBittorrent (downloads) → Plex (streaming)
                                                                            → Bazarr (Hebrew subs)
Telegram Bot ↔ Sonarr/Radarr/qBittorrent/Plex
Web Dashboard ↔ Sonarr/Radarr/qBittorrent/Bazarr
```

## Server Access
- **Host:** 192.168.0.148
- **SSH:** `sshpass -p 'Kuntz876@!' ssh -o StrictHostKeyChecking=no amram@192.168.0.148`
- **Sudo:** `echo 'Kuntz876@!' | sudo -S <command>`
- **Project path:** /home/amram/amram-media
- **SSD:** /mnt/ssd (465GB, ext4, auto-mounted via fstab)

## Services

| Service | Port | Container Network | Purpose |
|---------|------|-------------------|---------|
| Plex | 32400 | host | Media streaming |
| Sonarr | 8989 | media-net | TV series management |
| Radarr | 7878 | media-net | Movie management |
| qBittorrent | 8080 | media-net | Torrent downloads |
| Bazarr | 6767 | media-net | Hebrew subtitles (OpenSubtitles + Ktuvit) |
| Prowlarr | 9696 | media-net | Indexer management |
| Telegram Bot | - | media-net | Telegram control interface |
| Web Dashboard | 8000 | media-net | Web UI |

## Key Paths (inside containers)
- `/tv` → /mnt/ssd/Series
- `/movies` → /mnt/ssd/Movies
- `/downloads` → /mnt/ssd/Downloads
- `/lectures` → /mnt/ssd/Lectures
- `/config` → /home/amram/amram-media/config/<service>

## Deployment
```bash
# Deploy all services
cd /home/amram/amram-media && docker compose up -d --build

# Rebuild only telegram-bot after code changes
scp -r telegram-bot/bot amram@192.168.0.148:/home/amram/amram-media/telegram-bot/
ssh amram@192.168.0.148 "cd /home/amram/amram-media && docker compose up -d --build telegram-bot"
```

## Hebrew Subtitles
- Bazarr auto-searches Hebrew subs via OpenSubtitles and Ktuvit
- Hebrew language profile (ID: 1) is default for all series and movies
- Plex user setting: subtitles always enabled, Hebrew preferred

## Plex Auto-Scan
- Cron: every 5 minutes scans all libraries
- Sonarr/Radarr: notify Plex on download/rename/delete (via gateway IP 172.18.0.1)
- Plex: filesystem event monitoring + scheduled scan enabled

## Server Configuration
- Lid close: ignored (logind.conf)
- Sleep/suspend/hibernate: masked
- Power profile: power-saver (persisted via systemd service)
- Fans: auto-managed, quiet at idle

## Git & GitHub
- **Repo:** https://github.com/WhyNotBoth953/AmramMedia
- **Remote:** `origin` is configured with auth token in URL
- **Branches:** `main` (default on GitHub), `master` (local working branch)
- **Commit & Push:**
```bash
git add <files>
git commit -m "message"
git push origin master
```
- **Credentials:** stored in `../github.txt` (username + PAT) — NOT tracked in git

## Notes
- Plex uses `network_mode: host` — other containers reach it via Docker bridge gateway (172.18.0.1:32400)
- qBittorrent: upload limited to 1 MB/s, max ratio 1.0, max seed time 24h, auto-remove
- Israeli content (e.g., Ramzor) needs Fuzer.xyz indexer — requires browser cookie (reCAPTCHA protected login)
- `.env` contains secrets and is NOT tracked in git
