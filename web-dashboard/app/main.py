import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers import dashboard, downloads, movies, search, series, system, wishlist

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

app = FastAPI(title="AmramMedia Dashboard")

app.include_router(dashboard.router)
app.include_router(movies.router)
app.include_router(series.router)
app.include_router(downloads.router)
app.include_router(search.router)
app.include_router(system.router)
app.include_router(wishlist.router)

STATIC_DIR = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root():
    return FileResponse(str(STATIC_DIR / "index.html"))
