import asyncio

from fastapi import APIRouter, Query

from app.services.radarr import radarr
from app.services.sonarr import sonarr

router = APIRouter()


def _shape_movie_result(m: dict) -> dict:
    poster = ""
    for img in m.get("images", []):
        if img.get("coverType") == "poster":
            poster = img.get("remoteUrl", "") or img.get("url", "")
    return {
        "type": "movie",
        "title": m.get("title", ""),
        "year": m.get("year", 0),
        "overview": (m.get("overview", "") or "")[:200],
        "tmdbId": m.get("tmdbId", 0),
        "poster": poster,
    }


def _shape_series_result(s: dict) -> dict:
    poster = ""
    for img in s.get("images", []):
        if img.get("coverType") == "poster":
            poster = img.get("remoteUrl", "") or img.get("url", "")
    return {
        "type": "series",
        "title": s.get("title", ""),
        "year": s.get("year", 0),
        "overview": (s.get("overview", "") or "")[:200],
        "seasonCount": s.get("seasonCount", 0),
        "tvdbId": s.get("tvdbId", 0),
        "poster": poster,
    }


@router.get("/api/search")
async def search(q: str = Query(..., min_length=1)):
    movies, series = await asyncio.gather(
        radarr.search(q),
        sonarr.search(q),
        return_exceptions=True,
    )

    results = []
    if isinstance(movies, list):
        results.extend(_shape_movie_result(m) for m in movies[:5])
    if isinstance(series, list):
        results.extend(_shape_series_result(s) for s in series[:5])

    return results
