from abc import ABC, abstractmethod
from typing import Any
import logging

from elasticsearch import (
    AsyncElasticsearch,
    NotFoundError,
    ConnectionError as ESConnectionError,
)
from elasticsearch_dsl import AsyncSearch, Q

logger = logging.getLogger(__name__)


class DBManager(ABC):
    """Абстрактный класс для управления базой данных."""

    def __init__(self, db_client: Any, db_name: str):
        self.db_client = db_client
        self.db_name = db_name

    @abstractmethod
    async def get_object_by_id(self, object_id: str) -> dict[str, Any] | None:
        """Получение объекта по ID."""

    @abstractmethod
    async def get_objects_by_query(
        self,
        query: str | None = None,
        fields: list[str] | None = None,
        sort: str = "-imdb_rating",
        page_size: int = 10,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """Получение объектов по запросу."""


class ElasticManager(DBManager):
    """Класс для управления Elasticsearch."""

    def __init__(self, es_client: AsyncElasticsearch, index_name: str):
        super().__init__(es_client, index_name)
        self.es_client = es_client
        self.index_name = index_name

    async def get_object_by_id(self, object_id: str) -> dict[str, Any] | None:
        """Получение объекта из Elasticsearch по ID."""
        try:
            doc = await self.es_client.get(index=self.index_name, id=object_id)
            logger.info("Документ с ID {} успешно найден.".format(object_id))
            return doc["_source"]
        except NotFoundError:
            logger.warning("Документ с ID {} не найден.".format(object_id))
            return None
        except ESConnectionError as e:
            logger.error(
                "Ошибка подключения к Elasticsearch при поиске ID {}: {}".format(
                    object_id, e
                )
            )
            return None
        except Exception as e:
            logger.exception(
                "Неизвестная ошибка при поиске ID {}: {}".format(object_id, e)
            )
            return None

    async def get_objects_by_query(
        self,
        query: str | None = None,
        fields: list[str] | None = None,
        sort: str = "-imdb_rating",
        page_size: int = 10,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """
        Получение списка объектов из Elasticsearch по запросу.

        :param query: Поисковая строка.
        :param fields: Поля, в которых производится поиск.
        :param sort: Поле для сортировки (например, '-imdb_rating').
        :param page_size: Количество записей на странице.
        :param page: Номер страницы.
        :return: Список объектов в виде словарей.
        """
        fields = fields or [
            "title"
        ]  # Устанавливаем значение по умолчанию, если поля не указаны
        try:
            search = await self._generate_query(
                query=query, fields=fields, sort=sort, page_size=page_size, page=page
            )
            response = await search.execute()
            documents = [hit.to_dict() for hit in response]
            logger.info(
                "Запрос выполнен успешно. Найдено {} объектов.".format(len(documents))
            )
            return documents
        except ESConnectionError as e:
            logger.error(
                "Ошибка подключения к Elasticsearch при выполнении запроса: {}".format(
                    e
                )
            )
            return []
        except Exception as e:
            logger.exception("Неизвестная ошибка при выполнении запроса: {}".format(e))
            return []

    async def _generate_query(
        self,
        query: str | None = None,
        fields: list[str] | None = None,
        sort: str = "-imdb_rating",
        page_size: int = 10,
        page: int = 1,
    ) -> AsyncSearch:
        """
        Генерация запроса для Elasticsearch с учетом поисковой фразы, полей, сортировки и пагинации.

        :param query: Поисковая строка.
        :param fields: Поля для поиска.
        :param sort: Поле для сортировки с направлением (например, '-imdb_rating').
        :param page_size: Количество записей на странице.
        :param page: Номер страницы.
        :return: Сгенерированный объект запроса AsyncSearch.
        """
        search = AsyncSearch(using=self.es_client, index=self.index_name)

        if query and fields:
            must_queries = [Q("match", **{field: query}) for field in fields if field]
            search = search.query("bool", must=must_queries)
            logger.debug("Сформирован запрос с поисковой строкой: {}".format(query))
        else:
            search = search.query(Q("match_all"))
            logger.debug("Сформирован запрос для получения всех документов.")

        for sort_field in sort.split(","):
            field = sort_field.lstrip("-")
            order = "desc" if sort_field.startswith("-") else "asc"
            search = search.sort({field: {"order": order}})
            logger.debug("Добавлена сортировка: {} ({}).".format(field, order))

        search = search[(page - 1) * page_size : page * page_size]
        return search
