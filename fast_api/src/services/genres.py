import logging
from functools import lru_cache
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis


from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.services.db_managers import DBManager, ElasticManager
from src.services.redis_service import AbstractCache, RedisCache
from src.models.genre import Genre


logger = logging.getLogger(__name__)


class GenreService:
    def __init__(self, redis: AbstractCache, db_client: DBManager):
        self.redis = redis
        self.db_client = db_client

    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        genre_key = self.redis.get_query_key(genre_id)
        genre = await self.redis.get_object(genre_key)
        if genre is None:
            genre = await self.db_client.get_object_by_id(genre_id)
            if genre is None:
                logger.warning("Не найден фильм с id %s.", genre_id)
                return None
            await self.redis.set_object(object_key=genre_key, value=genre)
        return Genre(**genre)

    async def get_all_genres(
        self, sort: str = "name", page: int = 1, page_size: int = 10
    ) -> list[Genre]:
        genres_key = self.redis.get_query_key(sort=sort, page_size=page_size, page=page)
        genres = await self.redis.get_object(object_key=genres_key)
        if genres is None:
            genres = await self.db_client.get_objects_by_query()
            if genres is None:
                logger.warning(
                    "Не найдено данных при запросе с параметрами: %s.", genres_key
                )
                return None
            await self.redis.set_object(object_key=genres_key, value=genres)
        return genres


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    redis_client = RedisCache(redis_client=redis)
    elastic_manager = ElasticManager(es_client=elastic, index_name="genres")
    return GenreService(redis_client, elastic_manager)
