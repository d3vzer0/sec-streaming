from datetime import datetime, timedelta
import dateparser
import os

DEFAULT_TIMEZONE = os.getenv('DEFAULT_TIMEZONE', 'UTC')
DEFAULT_NO_UPDATED = os.getenv('DEFAULT_NO_UPDATED', 3600)
DEFAULT_FIRST_SEEN = os.getenv('DEFAULT_FIRST_SEEN', 604800)

async def get_items(content, cache):
    current_date = datetime.utcnow()

    # Get the previously executed date by URL or default 
    saved_checkpoint = await cache.get(content['link'], encoding='utf-8')
    last_updated = dateparser.parse(saved_checkpoint, settings={'TIMEZONE': DEFAULT_TIMEZONE, 'RETURN_AS_TIMEZONE_AWARE': True}) if \
        saved_checkpoint else (current_date - timedelta(seconds=DEFAULT_FIRST_SEEN))

    # Get latest published/updated date for rss feed or default
    parsed_date = dateparser.parse(content['updated'], settings={'TIMEZONE': DEFAULT_TIMEZONE, 'RETURN_AS_TIMEZONE_AWARE': True}) if \
        content['updated'] else (current_date - timedelta(seconds=DEFAULT_NO_UPDATED))

    # Return items if feed has been updated
    all_items = content['items'] if parsed_date > last_updated else []
    return all_items