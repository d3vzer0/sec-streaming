class RSSFeed:
    def __init__(self, data, feed):
        self.data = data
        self.feed = feed

    def __strip_items(item):
        return {
            'title': item['title'],
            'link': item['link'],
            'description': item['description'],
            'author': item.get('author'),
            'summary': item.get('summary'),
            'id': item['id'],
            'published': item['updated'],
            'tags': [tag['term'] for tag in item.get('tags', [])],
            'category': item.get('category'),
            'content': item.get('content', [{'value':''}])[0]['value']
        }

    @property
    def stripped(self):
        return {
            'title': self.data['channel']['title'],
            'link': self.data['channel'].get('link', self.feed.url),
            'updated': self.data['channel'].get('updated'),
            'items': [RSSFeed.__strip_items(item) for item in self.data['items']]
        }
