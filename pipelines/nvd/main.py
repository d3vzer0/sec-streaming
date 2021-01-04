
from pipelines.app import app
from datetime import datetime, timedelta
from .utils.cves import NVD
import os
# import aioredis

DEFAULT_FETCH_DAYS = os.getenv('DEFAULT_FETCH_DAYS', 7)
DEFAULT_MAX_RESULTS = os.getenv('DEFAULT_MAX_RESULTS', 2000)
TARGET_TOPIC_NVD = os.getenv('TARGET_TOPIC_NVD', 'NVD_cves')
TARGET_CACHE_PREFIX = os.getenv('TARGET_CACHE_PREFIX', 'NVD')

# Topics to read/write feed sources and individual RSS items
nvd_topic = app.topic(TARGET_TOPIC_NVD)

async def get_latest_cves(cache=None):
    init_date = datetime.utcnow() - timedelta(days=DEFAULT_FETCH_DAYS)
    init_date_fmt = init_date.strftime('%Y-%m-%dT%H:%M:%S:000 UTC-00:00')
    params = { 'resultsPerPage': DEFAULT_MAX_RESULTS,
        'modStartDate': init_date_fmt }

    async with NVD(params) as nvd:
        all_cves = await nvd.cves
        for cve in all_cves:
            await nvd_topic.send(value=cve.dict())
        return all_cves

@app.timer(30.0)
async def start_cves_download():
    # cache = await aioredis.create_redis_pool('redis://localhost')
    await get_latest_cves()

