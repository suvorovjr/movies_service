from datetime import datetime
from typing import Generator

from psycopg import connection as _connection
from psycopg import ServerCursor
from psycopg.rows import class_row

from elasticsearch_dsl import Document

from .queries import queries


def get_index_data(
    conn: _connection, index: Document, last_sync_state: datetime, batch_size: int = 100
) -> Generator[list, None, None]:

    with ServerCursor(conn, 'fetcher', row_factory=class_row(index)) as cursor:
        cursor.execute(queries[index], (last_sync_state,))
        while results := cursor.fetchmany(size=batch_size):
            yield results
