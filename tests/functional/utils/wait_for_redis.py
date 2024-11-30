import time

from redis import Redis
from redis.exceptions import ConnectionError

from tests.functional.settings import test_settings

if __name__ == '__main__':
    redis_client = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    while True:
        try:
            if redis_client.ping():
                break
        except ConnectionError:
            time.sleep(1)