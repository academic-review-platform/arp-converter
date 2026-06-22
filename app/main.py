from fastapi import FastAPI

from app.core.config import settings


def create_app() -> FastAPI:
    return FastAPI(
        title=settings.project_name,
        version=settings.version,
        description=settings.description,
    )


app = create_app()
