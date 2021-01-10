from faust.models.fields import DatetimeField
from dateutil.parser import parse as parse_date
from typing import List, Optional
import datetime
import faust

class GetContentModel(faust.Record):
    link: str


class RssItemModel(faust.Record, coerce=True, date_parser=parse_date):
    title: str
    description: str
    link: str
    summary: str
    id: str
    published: datetime = DatetimeField(date_parser=parse_date)
    content: str
    tags: List[str]
    author: str


class RssFeedModel(faust.Record):
    title: str
    link: str


class RSSModel(faust.Record):
    item: RssItemModel
    feed: RssFeedModel


class SourceModel(faust.Record):
    provider: str
    category: str


class MainItemModel(faust.Record):
    rss: RSSModel
    source: SourceModel


class InitFeedModel(faust.Record):
    url: str
    provider: str
    category: str