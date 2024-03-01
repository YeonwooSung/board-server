from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

import os
from functools import cache
from pathlib import Path
import toml

# custom imports
from app.api.user import router as user_router
from app.api.health import router as health_router
from app.services.auth import AuthBearer
from app.redis import get_redis
from app.middlewares import RequestLogger, RequestID


@cache
def project_root() -> Path:
    """Find the project root directory by locating pyproject.toml."""
    base_dir = Path(__file__).parent

    for parent_directory in base_dir.parents:
        if (parent_directory / "pyproject.toml").is_file():
            return parent_directory
    raise FileNotFoundError("Could not find project root containing pyproject.toml")


def get_version_from_pyproject_toml() -> str:
    try:
        # Probably this is the pyproject.toml of a development install
        path_to_pyproject_toml = project_root() / "pyproject.toml"
    except FileNotFoundError:
        # Probably not a development install
        path_to_pyproject_toml = None

    if path_to_pyproject_toml is not None:
        pyproject_version = toml.load(path_to_pyproject_toml)["tool"]["poetry"]["version"]
        return pyproject_version
    else:
        return os.getenv("VERSION", "x.x.x")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the redis connection
    app.state.redis = await get_redis()
    yield
    # close redis connection and release the resources
    app.state.redis.close()


def init_app(use_rate_limiter:bool=False) -> FastAPI:
    version = get_version_from_pyproject_toml()
    app = FastAPI(title="Board Server", version=version, lifespan=lifespan)
    if use_rate_limiter:
        from app.utils.ratelimitter import limiter
        app.state.limiter = limiter

    # add middlewares
    app.add_middleware(
        ProxyHeadersMiddleware, trusted_hosts="*"
    )  # add proxy headers to prevent logging IP address of the proxy server instead of the client
    app.add_middleware(GZipMiddleware, minimum_size=500)  # add gzip compression

    # add custom middlewares
    app.add_middleware(RequestLogger)
    app.add_middleware(RequestID)

    return app


def add_api_routers(app:FastAPI, add_static_files: bool = False) -> None:
    app.include_router(user_router)
    app.include_router(health_router, prefix="/v1/public/health", tags=["Health, Public"])
    app.include_router(health_router, prefix="/v1/health", tags=["Health, Bearer"], dependencies=[Depends(AuthBearer())])

    if add_static_files:
        # set up static files (css, js, images, etc.)
        app.mount("/public", StaticFiles(directory="public"), name="public")
