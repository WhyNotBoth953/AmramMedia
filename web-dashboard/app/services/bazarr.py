import aiohttp

from app.config import BAZARR_API_KEY, BAZARR_URL


class BazarrClient:
    def __init__(self):
        self.base_url = BAZARR_URL.rstrip("/")

    async def _get(self, endpoint: str, params: dict | None = None) -> list | dict:
        p = {"apikey": BAZARR_API_KEY}
        if params:
            p.update(params)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/{endpoint}",
                params=p,
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def get_wanted_movies(self) -> list[dict]:
        """Get movies with missing subtitles."""
        result = await self._get("movies/wanted", params={"length": 50})
        return result.get("data", [])

    async def get_wanted_series(self) -> list[dict]:
        """Get episodes with missing subtitles."""
        result = await self._get("episodes/wanted", params={"length": 50})
        return result.get("data", [])

    async def get_system_status(self) -> dict:
        """Get Bazarr system status."""
        return await self._get("system/status")


bazarr = BazarrClient()
