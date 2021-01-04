import os

config = {
    'stream': {
        'app': os.getenv('ST_STREAM_TYPE', 'pipelines.nvd'),
        'host': os.getenv('ST_KAFKA_HOST', 'kafka://127.0.0.1:29092'),
        'partitions': os.getenv('ST_STREAM_PARTITIONS', 4),
        'store': os.getenv('ST_STREAM_STORE', 'memory://')
    }
}