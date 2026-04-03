import asyncio
import shutil

from fastapi import APIRouter

from app.config import SSD_MOUNT_PATH
from app.services.qbittorrent import qbt
from app.services.radarr import radarr
from app.services.sonarr import sonarr

router = APIRouter()


@router.get("/api/dashboard")
async def get_dashboard():
    movies, series, torrents, transfer = await asyncio.gather(
        radarr.get_movies(),
        sonarr.get_series(),
        qbt.get_torrents("downloading"),
        qbt.get_transfer_info(),
        return_exceptions=True,
    )

    result = {}

    if isinstance(movies, list):
        active_movies = [m for m in movies if m.get("monitored")]
        result["movies"] = {
            "total": len(active_movies),
            "downloaded": sum(1 for m in active_movies if m.get("hasFile")),
        }
    else:
        result["movies"] = {"total": 0, "downloaded": 0, "error": str(movies)}

    if isinstance(series, list):
        active_series = [s for s in series if s.get("monitored")]
        total_eps = sum(s.get("statistics", {}).get("totalEpisodeCount", 0) for s in active_series)
        have_eps = sum(s.get("statistics", {}).get("episodeFileCount", 0) for s in active_series)
        result["series"] = {
            "total": len(active_series),
            "totalEpisodes": total_eps,
            "downloadedEpisodes": have_eps,
        }
    else:
        result["series"] = {"total": 0, "totalEpisodes": 0, "downloadedEpisodes": 0, "error": str(series)}

    if isinstance(torrents, list):
        result["downloads"] = {"active": len(torrents)}
    else:
        result["downloads"] = {"active": 0, "error": str(torrents)}

    if isinstance(transfer, dict):
        result["transfer"] = {
            "downloadSpeed": transfer.get("dl_info_speed", 0),
            "uploadSpeed": transfer.get("up_info_speed", 0),
        }
    else:
        result["transfer"] = {"downloadSpeed": 0, "uploadSpeed": 0}

    try:
        usage = shutil.disk_usage(SSD_MOUNT_PATH)
        result["disk"] = {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": round(usage.used / usage.total * 100, 1),
        }
    except Exception:
        result["disk"] = {"total": 0, "used": 0, "free": 0, "percent": 0}

    return result
