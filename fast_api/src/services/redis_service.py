import json
import logging
from abc import ABC, abstractmethod

from typing import Any
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class AbstractCache(ABC):
    """
    Абстрактный класс для кэширования объектов.
    """

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    @abstractmethod
    async def get_object(self, object_key: str) -> dict[str, Any] | list[dict[str, Any]]:
        """
        Получить объект из кэша по ключу.
        :param object_key: Ключ объекта.
        :return: Объект в формате dict или None, если ключ не найден.
        """
        pass

    @abstractmethod
    async def set_object(self, object_key: str, value: dict[str, Any] | list[dict[str, Any]], expire: int = 60) -> None:
        """
        Установить объект в кэш.
        :param object_key: Ключ объекта.
        :param value: Сохраняемое значение в формате dict.
        :param expire: Время жизни кэша (в секундах).
        """
        pass

    @abstractmethod
    def get_query_key(self, *args, **kwargs) -> str:
        """
        Генерировать ключ для запроса на основе параметров.
        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        :return: Сформированный ключ.
        """
        pass


class RedisCache(AbstractCache):
    """
    Реализация кэширования с использованием Redis.
    """

    def __init__(self, redis_client: Redis):
        super().__init__(redis_client)

    async def get_object(self, object_key: str) -> dict[str, Any] | None:
        """
        Получить объект из Redis по ключу.
        :param object_key: Ключ объекта.
        :return: Объект в формате dict или None, если ключ не найден.
        """
        try:
            value = await self.redis_client.get(object_key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.error('Ошибка при получении объекта с ключом {}: {}'.format(object_key, e))
            return None

    async def set_object(self, object_key: str, value: dict[str, Any] | list[dict[str, Any]], expire: int = 60) -> None:
        """
        Установить объект в Redis.
        :param object_key: Ключ объекта.
        :param value: Сохраняемое значение.
        :param expire: Время жизни кэша (в секундах).
        """
        try:
            await self.redis_client.set(
                name=object_key,
                value=json.dumps(value),
                ex=expire  # Время жизни ключа
            )
        except Exception as e:
            logger.error('Ошибка при установке объекта с ключом {}: {}'.format(object_key, e))

    def get_query_key(self, *args, **kwargs) -> str:
        """
        Генерировать ключ для кэширования запросов.
        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        :return: Сформированный ключ.
        """

        key = ':'.join(map(str, args))
        if kwargs:
            key += ':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()))
        return key
