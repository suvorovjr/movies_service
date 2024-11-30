import logging
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.services.db_managers import ElasticManager, DBManager
from src.models.film import Film
from src.services.redis_service import RedisCache, AbstractCache

logger = logging.getLogger(__name__)


class FilmService:
    def __init__(self, cache_manager: AbstractCache, db_manager: DBManager):
        self.cache_manager = cache_manager
        self.db_manager = db_manager

    async def get_film_list(
            self,
            sort: str = '-imdb_rating',
            page_size: int = 10,
            page: int = 1,
    ) -> list[Film] | None:
        """ Получаем список фильмов, кэшируем результаты. """

        key = self.cache_manager.get_query_key(sort, page_size, page)
        films_list = await self.cache_manager.get_object(object_key=key)
        if films_list is None:
            films_list = await self.db_manager.get_objects_by_query(sort=sort, page_size=page_size, page=page)
            if not films_list:
                return None
            await self.cache_manager.set_object(object_key=key, value=films_list)
        return [Film(**film) for film in films_list]

    async def get_by_id(self, film_id: str) -> Film | None:
        """ Получаем фильм по ID с кэшированием. """

        film = await self.cache_manager.get_object(object_key=film_id)
        if film is None:
            film = await self.db_manager.get_object_by_id(film_id)
            if film is None:
                return None
            else:
                await self.cache_manager.set_object(object_key=film_id, value=film)
        return Film(**film)

    async def get_films_by_query(
            self,
            query: str,
            sort: str = '-imdb_rating',
            page_size: int = 10,
            page: int = 1
    ) -> list[Film] | None:
        """ Получаем фильмы по запросу. """
        search_fields = ['title', 'description']
        key = self.cache_manager.get_query_key(query, sort, page_size, page)
        films_by_query = await self.cache_manager.get_object(object_key=key)
        if films_by_query is None:
            films_by_query = await self.db_manager.get_objects_by_query(query=query, fields=search_fields, sort=sort,
                                                                        page_size=page_size, page=page)
            if films_by_query is None:
                return None
            else:
                await self.cache_manager.set_object(object_key=key, value=films_by_query)
        return [Film(**film) for film in films_by_query]


@lru_cache
def get_film_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
        redis: Redis = Depends(get_redis),
) -> FilmService:
    elastic_manager = ElasticManager(elastic, 'movies')
    redis_manager = RedisCache(redis_client=redis)
    return FilmService(cache_manager=redis_manager, db_manager=elastic_manager)
