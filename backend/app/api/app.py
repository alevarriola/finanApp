import contextlib
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aioinject.ext.fastapi import AioInjectMiddleware

from app.core.config import get_settings
from app.core.container import create_container
from app.graphql.schemas.schema import create_graphql_router


def create_app() -> FastAPI:
    settings = get_settings()
    container = create_container()

    @contextlib.asynccontextmanager
    async def lifespan(_app: FastAPI):
        yield

    app = FastAPI(
        title=settings.app_name,
        openapi_url=None,
        lifespan=lifespan,
    )

    app.add_middleware(AioInjectMiddleware, container=container)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(create_graphql_router(container), prefix="/graphql")

    @app.get("/api/health")
    def health_check():
        return {"status": "ok", "app": settings.app_name}

    @app.middleware("http")
    async def add_process_time_header(request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Process-Time-Ms"] = f"{ms}ms"
        return response

    return app
