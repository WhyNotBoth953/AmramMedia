import aiohttp

from bot.config import BAZARR_API_KEY, BAZARR_URL


class BazarrClient:
    def __init__(self):
        self.base_url = BAZARR_URL.rstrip("/")
        self.api_key = BAZARR_API_KEY

    async def _get(self, endpoint: str, params: dict | None = None) -> dict:
        p = {"apikey": self.api_key}
        if params:
            p.update(params)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/{endpoint}",
                params=p,
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def get_wanted_counts(self) -> dict:
        """Return count of movies and episodes missing subtitles."""
        movies_result = await self._get("movies/wanted", params={"length": 1})
        episodes_result = await self._get("episodes/wanted", params={"length": 1})
        return {
            "movies": movies_result.get("total", 0),
            "episodes": episodes_result.get("total", 0),
        }
