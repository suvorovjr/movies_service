import time
from datetime import datetime
from typing import Generator, Any

import pytz
from dateutil import parser
from elasticsearch.helpers import bulk
from elasticsearch_dsl import connections

import psycopg
from psycopg.conninfo import make_conninfo

from documents.movie import Movie
from documents.genre import Genre
from documents.person import Person
from documents.load_data import get_index_data

from helpers.backoff_func_wrapper import backoff
from logger import logger
from settings import settings
from state_manager.json_file_storage import JsonFileStorage
from state_manager.state_manager import StateManager


@backoff(0.1, 2, 10, logger)
def _send_to_es(es_load_data:  Generator[dict[str, Any], Any, None]):
    bulk(
        connections.get_connection(),
        es_load_data,
    )


def get_state():
    state_manager = StateManager(JsonFileStorage(logger=logger))

    last_sync_state = state_manager.get_state('movie_index_last_sync_state')

    if last_sync_state is None:
        last_sync_state = pytz.UTC.localize(datetime.min)
    else:
        last_sync_state = parser.isoparse(last_sync_state)
    return last_sync_state, state_manager


indexes = [
    Genre,
    Movie,
    Person
]


def update_indexs():
    connections.create_connection(hosts=settings.elasticsearch_settings.get_host())
    last_sync_state, state_manager = get_state()

    database_settings = settings.database_settings.get_dsn()
    dsn = make_conninfo(**database_settings)

    with psycopg.connect(dsn) as conn:

        for index in indexes:
            index.init()

            for rows in get_index_data(conn, index, last_sync_state, 100):
                es_load_data = (dict(d.to_dict(True, skip_empty=False), **{'_id': d.id}) for d in rows)
                _send_to_es(es_load_data)

    state_manager.set_state('movie_index_last_sync_state', last_sync_state.isoformat())


if __name__ == '__main__':
    while True:
        try:
            update_indexs()
            time.sleep(60)
        except Exception as e:
            logger.exception(e)
