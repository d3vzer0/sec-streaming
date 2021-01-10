
from pipelines.app import app
from datetime import datetime, timedelta
from .utils.cves import NVD
from .utils.transforms import CVE
import os
# import aioredis

''' Global options '''
DEFAULT_FETCH_DAYS = os.getenv('DEFAULT_FETCH_DAYS', 7)
DEFAULT_MAX_RESULTS = os.getenv('DEFAULT_MAX_RESULTS', 2000)
TARGET_TOPIC_NVD = os.getenv('TARGET_TOPIC_NVD', 'NVD_raw')
TARGET_TOPIC_DETAILS = os.getenv('TARGET_TOPIC_DETAILS', 'NVD_cve_details')
TARGET_TOPIC_IMPACTED = os.getenv('TARGET_TOPIC_IMPACTED', 'NVD_cve_impacted')
TARGET_TOPIC_REFS = os.getenv('TARGET_TOPIC_REFS', 'NVD_cve_refs')
TARGET_CACHE_PREFIX = os.getenv('TARGET_CACHE_PREFIX', 'NVD')

''' Topics to read/write raw and parsed CVEs '''
nvd_topic = app.topic(TARGET_TOPIC_NVD)
cve_details_topic = app.topic(TARGET_TOPIC_DETAILS)
cve_impacted_topic = app.topic(TARGET_TOPIC_IMPACTED)
cve_refs_topic = app.topic(TARGET_TOPIC_REFS)

async def get_latest_cves(cache=None):
    ''' Get the latest CVEs frtom the NVD API '''
    init_date = datetime.utcnow() - timedelta(days=DEFAULT_FETCH_DAYS)
    init_date_fmt = init_date.strftime('%Y-%m-%dT%H:%M:%S:000 UTC-00:00')
    params = { 'resultsPerPage': DEFAULT_MAX_RESULTS,
        'modStartDate': init_date_fmt }

    async with NVD(params) as nvd:
        all_cves = await nvd.cves
        for cve in all_cves:
            await nvd_topic.send(value=cve.dict())
        return all_cves

@app.agent(nvd_topic)
async def parse_cve_details(stream):
    ''' Prase CVE details using ECS schema'''
    async for value in stream:
        cve_object = CVE(cve=value)
        await cve_details_topic.send(value=cve_object.details)
        yield cve_object

@app.agent(nvd_topic)
async def parse_cve_impacted(stream):
    ''' Split CVEs to impacted products using ECS schema'''
    async for value in stream:
        cve_object = CVE(cve=value)
        for cpe in cve_object.impacted:
            await cve_impacted_topic.send(value=cpe)
        yield cve_object

@app.agent(nvd_topic)
async def parse_cve_refs(stream):
    ''' Split CVEs to references using ECS schema'''
    async for value in stream:
        cve_object = CVE(cve=value)
        for ref in cve_object.references:
            await cve_refs_topic.send(value=ref)
        yield cve_object

@app.timer(30.0)
async def start_cves_download():
    ''' Start polling latest CVES every X seconds '''
    # cache = await aioredis.create_redis_pool('redis://localhost')
    await get_latest_cves()
