from pipelines.app import app
from .models import InitFeedModel, RssItemModel
from .feeds import FEEDS
from .utils.items import get_items
from .utils.parser import RSSFeed
from .postprocessing.f5 import get_f5
from .postprocessing.generic import get_generic
import os
import aioredis
import feedparser

TARGET_TOPIC_FEEDS = os.getenv('TARGET_TOPIC_FEEDS', 'RSS_feeds_init')
TARGET_TOPIC_ITEMS = os.getenv('TARGET_TOPIC_ITEMS', 'RSS_items_post')
POSTPROCESSING = {
    'F5': get_f5
}

''' Last modified table to validate if item or feed has been updated '''
item_last_modified = app.Table('item-last-modified')

''' Topics to read/write feed sources and individual RSS items '''
items_topic = app.topic(TARGET_TOPIC_ITEMS, value_type=RssItemModel)
init_feeds_topic = app.topic(TARGET_TOPIC_FEEDS, value_type=InitFeedModel)


@app.agent(init_feeds_topic, concurrency=30)
async def read_feeds_init(stream):
    ''' Get latest RSS items from each provider '''
    cache = await aioredis.create_redis_pool('redis://localhost')
    async for value in stream:
        async with app.http_client.get(value.url) as response:
            content = await response.text()
            if not response: continue

        stripped_data = RSSFeed(feedparser.parse(content), value).stripped
        all_items = await get_items(stripped_data, cache)
        async for reply in POSTPROCESSING.get(value.provider, get_generic).map(all_items):
            await items_topic.send(value=reply)

@app.timer(10.0)
async def get_rss_items():
    ''' For each RSS provider send feed URL to topic '''
    for feed in FEEDS:
        await read_feeds_init.cast(value=feed)
