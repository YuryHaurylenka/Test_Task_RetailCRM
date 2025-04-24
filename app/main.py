from fastapi import FastAPI
from starlette.responses import RedirectResponse

from app.api import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.project_name, debug=settings.debug)
    app.include_router(api_router, prefix=settings.api_prefix)

    @app.get("/", include_in_schema=False)
    async def root() -> RedirectResponse:
        return RedirectResponse(url="/docs")

    return app


app = create_app()
