import logging.config
from .config import config
import faust

# logging.config.fileConfig("pipelines/logging.conf")
# logger = logging.getLogger("streamio")

app = faust.App('streamio', 
    broker=config['stream']['host'],
    autodiscover=[config['stream']['app']],
    stream_wait_empty=False,
    store=config['stream']['store'],
    partitions=config['stream']['partitions'],
    reply_create_topic=True,
    producer_max_request_size=2500000)


if __name__ == '__main__':
    app.main()