import aiohttp

from app.config import RADARR_API_KEY, RADARR_URL


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
        return await self._get("movie/lookup", params={"term": query})

    async def add_movie(self, movie: dict) -> dict:
        payload = {
            "title": movie["title"],
            "tmdbId": movie["tmdbId"],
            "year": movie.get("year", 0),
            "qualityProfileId": 1,
            "rootFolderPath": "/movies",
            "monitored": True,
            "addOptions": {"searchForMovie": True},
        }
        if "images" in movie:
            payload["images"] = movie["images"]
        return await self._post("movie", payload)

    async def get_movies(self) -> list[dict]:
        return await self._get("movie")

    async def get_queue(self) -> list[dict]:
        result = await self._get("queue", params={"pageSize": 50})
        return result.get("records", [])

    async def delete_movie(self, movie_id: int) -> None:
        await self._delete(f"movie/{movie_id}", params={"deleteFiles": "true"})


radarr = RadarrClient()
