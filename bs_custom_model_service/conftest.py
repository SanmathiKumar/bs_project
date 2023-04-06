import asyncio
from asyncio.events import AbstractEventLoop
import sys
from typing import Any, Generator, AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
import uuid
from unittest.mock import Mock

from bs_custom_model_service.settings import settings
from bs_custom_model_service.web.application import get_app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return 'asyncio'



@pytest.fixture
def fastapi_app(
    
) -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    application = get_app()
    return application  # noqa: WPS331


@pytest.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
            yield ac
