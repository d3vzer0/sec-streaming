from pipelines.app import app
from pipelines.rss.models import RssItemModel
from typing import AsyncIterable
from faust import StreamT
import re

BASE_URI = 'https://api-u.f5.com/support/kb-articles'

# Topic containing F5 articles to download
content_topic = app.topic('RSS_items_pre_f5', value_type=RssItemModel)

@app.agent(content_topic, concurrency=50)
async def get_f5(stream: StreamT[float]) -> AsyncIterable[float]:
    kb_pattern = re.compile('(?i)(K\d{8})')
    async for value in stream:
        get_kb = kb_pattern.search(value.link)
        uri = f'{BASE_URI}/{get_kb.group()}?cacheFlag=false'
        async with app.http_client.get(uri) as response:
            content = await response.json()
            value.content = '\n\n'.join([f'<h2>{item["title"]}</h2>\n{item["value"]}' 
                for item in content['content']])
            yield value