import logging

import aiohttp

from bot.config import RADARR_API_KEY, RADARR_URL

logger = logging.getLogger(__name__)


class RadarrClient:
    def __init__(self):
        self.base_url = RADARR_URL.rstrip("/")
        self.headers = {"X-Api-Key": RADARR_API_KEY}

    async def _get(self, endpoint: str, params: dict | None = None) -> list | dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/v3/{endpoint}",
                headers=self.headers,
                params=params,
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def _post(self, endpoint: str, data: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/v3/{endpoint}",
                headers=self.headers,
                json=data,
            ) as resp:
                if resp.status >= 400:
                    body = await resp.json()
                    if isinstance(body, list) and body:
                        raise Exception(body[0].get("errorMessage", f"HTTP {resp.status}"))
                    raise Exception(f"HTTP {resp.status}")
                return await resp.json()

    async def _delete(self, endpoint: str, params: dict | None = None) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/api/v3/{endpoint}",
                headers=self.headers,
                params=params,
            ) as resp:
                resp.raise_for_status()

    async def search(self, query: str) -> list[dict]:
        """Search for movies by title."""
        return await self._get("movie/lookup", params={"term": query})

    async def add_movie(self, movie: dict) -> dict:
        """Add a movie to Radarr."""
        payload = {
            "title": movie["title"],
            "tmdbId": movie["tmdbId"],
            "year": movie.get("year", 0),
            "qualityProfileId": 1,
            "rootFolderPath": "/movies",
            "monitored": True,
            "addOptions": {"searchForMovie": True},
        }
        # Preserve images if available
        if "images" in movie:
            payload["images"] = movie["images"]
        return await self._post("movie", payload)

    async def get_movies(self) -> list[dict]:
        """Get all movies in library."""
        return await self._get("movie")

    async def get_queue(self) -> list[dict]:
        """Get download queue."""
        result = await self._get("queue", params={"pageSize": 50})
        return result.get("records", [])

    async def delete_movie(self, movie_id: int, delete_files: bool = True) -> None:
        """Delete a movie from Radarr."""
        await self._delete(
            f"movie/{movie_id}",
            params={"deleteFiles": str(delete_files).lower()},
        )

    async def get_root_folders(self) -> list[dict]:
        """Get configured root folders."""
        return await self._get("rootfolder")
