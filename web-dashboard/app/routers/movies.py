from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.radarr import radarr

router = APIRouter()


def _shape_movie(m: dict) -> dict:
    """Extract only the fields the frontend needs."""
    poster = ""
    fanart = ""
    for img in m.get("images", []):
        if img.get("coverType") == "poster":
            poster = img.get("remoteUrl", "") or img.get("url", "")
        elif img.get("coverType") == "fanart":
            fanart = img.get("remoteUrl", "") or img.get("url", "")
    return {
        "id": m.get("id"),
        "title": m.get("title", ""),
        "year": m.get("year", 0),
        "overview": m.get("overview", ""),
        "hasFile": m.get("hasFile", False),
        "sizeOnDisk": m.get("sizeOnDisk", 0),
        "tmdbId": m.get("tmdbId", 0),
        "poster": poster,
        "fanart": fanart,
        "added": m.get("added", ""),
        "monitored": m.get("monitored", False),
    }


@router.get("/api/movies")
async def get_movies():
    movies = await radarr.get_movies()
    return [_shape_movie(m) for m in movies]


@router.delete("/api/movies/{movie_id}")
async def delete_movie(movie_id: int):
    try:
        await radarr.delete_movie(movie_id)
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AddMovieRequest(BaseModel):
    tmdbId: int


@router.post("/api/movies")
async def add_movie(req: AddMovieRequest):
    try:
        results = await radarr.search(f"tmdb:{req.tmdbId}")
        movie = next((m for m in results if m.get("tmdbId") == req.tmdbId), None)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        added = await radarr.add_movie(movie)
        return _shape_movie(added)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
