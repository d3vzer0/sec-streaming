from pipelines.app import app
from pipelines.rss.models import RssItemModel
from typing import AsyncIterable
from faust import StreamT


# Topic containing generic articles to download
content_topic = app.topic('RSS_items_pre_generic', value_type=RssItemModel)

@app.agent(content_topic, concurrency=50)
async def get_generic(stream: StreamT[float]) -> AsyncIterable[float]:
    async for value in stream:
        async with app.http_client.get(value.link) as response:
            content = await response.text()
            value.content = content
            yield value