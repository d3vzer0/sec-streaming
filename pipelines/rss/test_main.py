from pipelines.app import app
from .main import read_feeds_init
from .postprocessing.f5 import get_f5
from unittest.mock import Mock
import pytest
import aioredis

FEEDS = [
    {   
        'provider': 'Example',
        'category': 'vendor',
        'url': 'https://localhost/rss',
    },
]

POSTPROCESSING = {
    'F5': get_f5
}

@pytest.fixture()
def test_app(event_loop):
    app.finalize()
    app.conf.store = 'memory://'
    app.flow_control.resume()
    return app

@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    def mock_create_redis_pool(*args, **kwargs):
        return None
    monkeypatch.setattr(aioredis, "create_redis_pool", mock_create_redis_pool)
    return monkeypatch

@pytest.mark.asyncio
async def test_read_feeds_init(event_loop):
    test = 'test'

