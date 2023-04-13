from fastapi import FastAPI
from fastapi.responses import UJSONResponse

from bs_custom_model_service.web.api.router import api_router
from bs_custom_model_service.web.lifetime import (register_startup_event,
                                                  register_shutdown_event)


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="bs_custom_model_service",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Adds startup and shutdown events.
    register_startup_event(app)
    register_shutdown_event(app)

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    return app
