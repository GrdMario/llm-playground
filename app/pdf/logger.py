import sys
import re

from loguru import logger


def scrub_redis_url_username_and_password(record):
    record['message'] = re.sub(r'redis://[^\s:]+:[^\s@]+', 'redis://****:****', record['message'])
    record['message'] = re.sub(r'rediss://[^\s:]+:[^\s@]+', 'rediss://****:****', record['message'])
    return record


logger.remove()
logger.add(sys.stderr, filter=scrub_redis_url_username_and_password)
