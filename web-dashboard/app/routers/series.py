import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.plex import plex
from app.services.qbittorrent import qbt
from app.services.sonarr import sonarr

logger = logging.getLogger(__name__)

router = APIRouter()


def _shape_series(s: dict) -> dict:
    """Extract only the fields the frontend needs."""
    poster = ""
    fanart = ""
    for img in s.get("images", []):
        if img.get("coverType") == "poster":
            poster = img.get("remoteUrl", "") or img.get("url", "")
        elif img.get("coverType") == "fanart":
            fanart = img.get("remoteUrl", "") or img.get("url", "")
    stats = s.get("statistics", {})
    return {
        "id": s.get("id"),
        "title": s.get("title", ""),
        "year": s.get("year", 0),
        "overview": s.get("overview", ""),
        "seasonCount": s.get("seasonCount", 0),
        "totalEpisodes": stats.get("totalEpisodeCount", 0),
        "downloadedEpisodes": stats.get("episodeFileCount", 0),
        "sizeOnDisk": stats.get("sizeOnDisk", 0),
        "tvdbId": s.get("tvdbId", 0),
        "poster": poster,
        "fanart": fanart,
        "added": s.get("added", ""),
        "monitored": s.get("monitored", False),
    }


@router.get("/api/series")
async def get_series():
    series = await sonarr.get_series()
    return [_shape_series(s) for s in series]


@router.delete("/api/series/{series_id}")
async def delete_series(series_id: int):
    try:
        # Get series title before deleting so we can clean up torrents
        all_series = await sonarr.get_series()
        series = next((s for s in all_series if s.get("id") == series_id), None)
        title = series.get("title", "") if series else ""

        await sonarr.delete_series(series_id)

        # Clean up related torrents from qBittorrent
        if title:
            removed = await qbt.delete_torrents_by_name(title)
            if removed:
                logger.info("Removed %d torrent(s) for '%s'", removed, title)

        # Trigger Plex library scan so the show disappears immediately
        await plex.scan_library()

        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AddSeriesRequest(BaseModel):
    tvdbId: int


@router.post("/api/series")
async def add_series(req: AddSeriesRequest):
    try:
        results = await sonarr.search(f"tvdb:{req.tvdbId}")
        series = next((s for s in results if s.get("tvdbId") == req.tvdbId), None)
        if not series:
            raise HTTPException(status_code=404, detail="Series not found")
        added = await sonarr.add_series(series)
        return _shape_series(added)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
