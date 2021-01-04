from .main import get_latest_cves, nvd_topic
from .schema import ResponseModel
from .utils.cves import NVD
from pipelines.app import app
from unittest.mock import MagicMock
import io
import json
import pytest
import aioredis

def util_load_json(path):
    with io.open(path, mode='r', encoding='utf-8') as f:
        return json.loads(f.read())

class NVDTest(MagicMock):
    def __init__(self):
        self.results = []

    @property   
    async def cves(self):
        dummy_results = util_load_json('pipelines/nvd/test_data/get_latest_cves_response.json')
        format_results = ResponseModel(**dummy_results)
        self.results += format_results.result.CVE_Items
        return self.results

    async def __aenter__(self, *args, **kwargs):
        return self

    async def __aexit__(self, *args, **kwargs):
        return self

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
    async def mock_topic(*args, **kwargs):
        return None

    monkeypatch.setattr(aioredis, "create_redis_pool", mock_create_redis_pool)
    monkeypatch.setattr(nvd_topic, "send", mock_topic)
    monkeypatch.setattr(NVD, "cves", NVDTest.cves)
    monkeypatch.setattr(NVD, "__aenter__", NVDTest.__aenter__)
    monkeypatch.setattr(NVD, "__aexit__", NVDTest.__aexit__)
    return monkeypatch

@pytest.mark.asyncio
async def test_get_latest_cves():
    latest_cves = await get_latest_cves()
    assert latest_cves
