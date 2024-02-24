import os

import redis
from api.loggers import RedisApiLogger
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()


class RedisConnection:
    def __init__(self, host, port, password, retries=1):
        self.host = os.environ.get('REDIS_HOST')
        self.port = port
        self.password = password

    def __enter__(self):
        # Code to set up resources or perform actions before the block

        self.redis_client = redis.StrictRedis(host=self.host, port=self.port, password=self.password,
                                              decode_responses=True)

        if self.redis_client.ping():
            return self.redis_client

    def __exit__(self, exc_type, exc_value, traceback):
        if isinstance(exc_value, Exception):
            RedisApiLogger.warning(f"redis connection failed: {exc_type}")
            RedisApiLogger.warning(f"redis connection failed message: {exc_value}")
        self.redis_client.close()
        return True


class RedisConnectioKeys(TypedDict):
    host: str
    port: str
    password: str
