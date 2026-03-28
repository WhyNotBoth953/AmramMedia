import logging
from datetime import datetime, timedelta

import aiohttp

from bot.config import SONARR_API_KEY, SONARR_URL

logger = logging.getLogger(__name__)


class SonarrClient:
    def __init__(self):
        self.base_url = SONARR_URL.rstrip("/")
        self.headers = {"X-Api-Key": SONARR_API_KEY}

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
        """Search for series by title."""
        return await self._get("series/lookup", params={"term": query})

    async def add_series(self, series: dict) -> dict:
        """Add a series to Sonarr."""
        payload = {
            "title": series["title"],
            "tvdbId": series["tvdbId"],
            "year": series.get("year", 0),
            "qualityProfileId": 1,
            "rootFolderPath": "/tv",
            "monitored": True,
            "seasonFolder": True,
            "addOptions": {
                "monitor": "all",
                "searchForMissingEpisodes": True,
            },
        }
        if "images" in series:
            payload["images"] = series["images"]
        if "seasons" in series:
            payload["seasons"] = series["seasons"]
        return await self._post("series", payload)

    async def get_series(self) -> list[dict]:
        """Get all series in library."""
        return await self._get("series")

    async def get_upcoming(self, days: int = 7) -> list[dict]:
        """Get upcoming episodes in the next N days."""
        start = datetime.now().strftime("%Y-%m-%d")
        end = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        return await self._get("calendar", params={"start": start, "end": end})

    async def get_queue(self) -> list[dict]:
        """Get download queue."""
        result = await self._get("queue", params={"pageSize": 50})
        return result.get("records", [])

    async def delete_series(self, series_id: int, delete_files: bool = True) -> None:
        """Delete a series from Sonarr."""
        await self._delete(
            f"series/{series_id}",
            params={"deleteFiles": str(delete_files).lower()},
        )
