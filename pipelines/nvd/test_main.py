from .main import (get_latest_cves, nvd_topic, parse_cve_details,
    cve_details_topic, cve_impacted_topic, cve_refs_topic,
    parse_cve_refs, parse_cve_impacted)
from .schema import ResponseModel
from .utils.cves import NVD
from pipelines.app import app
from unittest.mock import MagicMock, Mock, patch
import io
import json
import pytest
import aioredis

def util_load_json(path):
    with io.open(path, mode='r', encoding='utf-8') as f:
        return json.loads(f.read())

def example_cves():
    dummy_results = util_load_json('pipelines/nvd/test_data/get_latest_cves_response.json')
    format_results = ResponseModel(**dummy_results)
    return format_results.result.CVE_Items

class NVDTest(MagicMock):
    def __init__(self):
        self.results = []

    @property   
    async def cves(self):
        self.results += example_cves()
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
    monkeypatch.setattr(NVD, "cves", NVDTest.cves)
    monkeypatch.setattr(NVD, "__aenter__", NVDTest.__aenter__)
    monkeypatch.setattr(NVD, "__aexit__", NVDTest.__aexit__)
    monkeypatch.setattr(nvd_topic, "send", mock_topic)
    monkeypatch.setattr(cve_details_topic, "send", mock_topic)
    monkeypatch.setattr(cve_impacted_topic, "send", mock_topic)
    monkeypatch.setattr(cve_refs_topic, "send", mock_topic)
    return monkeypatch

@pytest.mark.asyncio
async def test_get_latest_cves():
    latest_cves = await get_latest_cves()
    assert latest_cves

@pytest.mark.asyncio()
async def test_parse_cve_details(test_app):
    async with parse_cve_details.test_context() as agent:
        for cve in example_cves():
            event = await agent.put(cve.dict())
            assert event

@pytest.mark.asyncio()
async def test_parse_cve_refs(test_app):
    async with parse_cve_refs.test_context() as agent:
        for cve in example_cves():
            event = await agent.put(cve.dict())
            assert event

@pytest.mark.asyncio()
async def test_parse_cve_impacted(test_app):
    async with parse_cve_impacted.test_context() as agent:
        for cve in example_cves():
            event = await agent.put(cve.dict())
            assert event
