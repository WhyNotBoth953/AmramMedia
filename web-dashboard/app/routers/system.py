import shutil

from fastapi import APIRouter

from app.config import SSD_MOUNT_PATH
from app.services.bazarr import bazarr
from app.services.sonarr import sonarr

router = APIRouter()


@router.get("/api/disk")
async def get_disk():
    usage = shutil.disk_usage(SSD_MOUNT_PATH)
    return {
        "total": usage.total,
        "used": usage.used,
        "free": usage.free,
        "percent": round(usage.used / usage.total * 100, 1),
    }


@router.get("/api/upcoming")
async def get_upcoming(days: int = 7):
    episodes = await sonarr.get_upcoming(days)
    return [
        {
            "seriesTitle": ep.get("series", {}).get("title", "Unknown"),
            "season": ep.get("seasonNumber", 0),
            "episode": ep.get("episodeNumber", 0),
            "title": ep.get("title", "TBA"),
            "airDate": ep.get("airDate", ""),
        }
        for ep in episodes
    ]


@router.get("/api/subtitles/wanted")
async def get_wanted_subtitles():
    try:
        movies = await bazarr.get_wanted_movies()
        series = await bazarr.get_wanted_series()
        return {
            "wantedMovies": len(movies),
            "wantedEpisodes": len(series),
            "movies": movies[:20],
            "episodes": series[:20],
        }
    except Exception as e:
        return {"wantedMovies": 0, "wantedEpisodes": 0, "error": str(e)}
