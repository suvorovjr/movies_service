from elasticsearch_dsl import (
    Document,
    Keyword,
    MetaField,
    Text,
)

from .index_settings import index_settings


class Genre(Document):
    id = Keyword()
    name = Text(analyzer='ru_en', fields={'raw': Keyword()})
    last_change_date = Keyword(index=False)

    class Index:
        name = 'genres'
        settings = index_settings

    class Meta:
        dynamic = MetaField('strict')
