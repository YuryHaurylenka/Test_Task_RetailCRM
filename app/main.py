from fastapi import FastAPI
from starlette.responses import RedirectResponse

from app.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.project_name,
    debug=settings.debug,
)

app.include_router(api_router)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")
