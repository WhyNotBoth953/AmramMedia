import asyncio
import logging

from fastapi import APIRouter, HTTPException

from app.services.plex import plex
from app.services.qbittorrent import qbt
from app.services.radarr import radarr
from app.services.sonarr import sonarr

logger = logging.getLogger(__name__)

router = APIRouter()


def _shape_movie(m: dict) -> dict:
    poster = ""
    for img in m.get("images", []):
        if img.get("coverType") == "poster":
            poster = img.get("remoteUrl", "") or img.get("url", "")
    return {
        "id": m.get("id"),
        "type": "movie",
        "title": m.get("title", ""),
        "year": m.get("year", 0),
        "overview": (m.get("overview", "") or "")[:200],
        "tmdbId": m.get("tmdbId", 0),
        "poster": poster,
        "added": m.get("added", ""),
    }


def _shape_series(s: dict) -> dict:
    poster = ""
    for img in s.get("images", []):
        if img.get("coverType") == "poster":
            poster = img.get("remoteUrl", "") or img.get("url", "")
    return {
        "id": s.get("id"),
        "type": "series",
        "title": s.get("title", ""),
        "year": s.get("year", 0),
        "overview": (s.get("overview", "") or "")[:200],
        "seasonCount": s.get("seasonCount", 0),
        "tvdbId": s.get("tvdbId", 0),
        "poster": poster,
        "added": s.get("added", ""),
    }


@router.get("/api/wishlist")
async def get_wishlist():
    movies, series = await asyncio.gather(
        radarr.get_movies(),
        sonarr.get_series(),
    )
    items = []
    items.extend(_shape_movie(m) for m in movies if not m.get("monitored"))
    items.extend(_shape_series(s) for s in series if not s.get("monitored"))
    items.sort(key=lambda x: x.get("added", ""), reverse=True)
    return items


@router.post("/api/wishlist/movie/{movie_id}/download")
async def download_movie(movie_id: int):
    try:
        await radarr.activate_movie(movie_id)
        return {"status": "downloading"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/wishlist/series/{series_id}/download")
async def download_series(series_id: int):
    try:
        await sonarr.activate_series(series_id)
        return {"status": "downloading"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/wishlist/movie/{movie_id}")
async def remove_movie(movie_id: int):
    try:
        await radarr.delete_movie(movie_id)
        return {"status": "removed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/wishlist/series/{series_id}")
async def remove_series(series_id: int):
    try:
        await sonarr.delete_series(series_id)
        return {"status": "removed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
