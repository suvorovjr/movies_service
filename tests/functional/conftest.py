import pytest_asyncio
import asyncio

@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

from .fixtures.connection import *
from .fixtures.es_data import *
