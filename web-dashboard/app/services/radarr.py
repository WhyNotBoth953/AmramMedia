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

    async def _put(self, endpoint: str, data: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{self.base_url}/api/v3/{endpoint}",
                headers=self.headers,
                json=data,
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def add_movie(self, movie: dict, monitored: bool = True) -> dict:
        payload = {
            "title": movie["title"],
            "tmdbId": movie["tmdbId"],
            "year": movie.get("year", 0),
            "qualityProfileId": 1,
            "rootFolderPath": "/movies",
            "monitored": monitored,
            "addOptions": {"searchForMovie": monitored},
        }
        if "images" in movie:
            payload["images"] = movie["images"]
        return await self._post("movie", payload)

    async def activate_movie(self, movie_id: int) -> dict:
        all_movies = await self.get_movies()
        movie = next((m for m in all_movies if m.get("id") == movie_id), None)
        if not movie:
            raise Exception("Movie not found")
        movie["monitored"] = True
        updated = await self._put(f"movie/{movie_id}", movie)
        await self._post("command", {"name": "MoviesSearch", "movieIds": [movie_id]})
        return updated

    async def get_movies(self) -> list[dict]:
        return await self._get("movie")

    async def get_queue(self) -> list[dict]:
        result = await self._get("queue", params={"pageSize": 50})
        return result.get("records", [])

    async def delete_movie(self, movie_id: int) -> None:
        await self._delete(f"movie/{movie_id}", params={"deleteFiles": "true"})


radarr = RadarrClient()
