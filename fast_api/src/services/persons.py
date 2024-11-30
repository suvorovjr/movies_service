from functools import lru_cache
import logging

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.services.redis_service import AbstractCache, RedisCache
from src.services.db_managers import DBManager, ElasticManager
from src.models.film import Person


logger = logging.getLogger(__name__)


class PersonService:
    def __init__(self, redis_client: AbstractCache, elastic_client: DBManager):
        self.redis_client = redis_client
        self.elastic_client = elastic_client

    async def get_person_by_id(self, person_id: str) -> Person | None:
        person_key = self.redis_client.get_query_key(person_id)
        person = await self.redis_client.get_object(person_key)
        if person is None:
            person = await self.elastic_client.get_object_by_id(person_id)
            if person is None:
                logger.warning("Не удалось получить персону по id %s", person_id)
                return None
            await self.redis_client.set_object(object_key=person_key, value=person)
        return person

    async def get_person_by_query(self, query, sort, page_size, page):
        pass

    async def get_person_list(self, sort, page_size, page):
        pass


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    redis_client = RedisCache(redis)
    elastic_client = ElasticManager(elastic, "person")
    return PersonService(redis_client=redis_client, elastic_client=elastic_client)
