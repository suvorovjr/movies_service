from elasticsearch_dsl import (
    Document,
    Keyword,
    MetaField,
    Text,
    Nested,
    InnerDoc,
)

from .index_settings import index_settings


class Films(InnerDoc):
    id = Keyword()
    roles = Text(analyzer='ru_en')

    class Meta:
        dynamic = MetaField('strict')


class Person(Document):
    id = Keyword()
    full_name = Text(analyzer='ru_en', fields={'raw': Keyword()})
    films = Nested(Films)
    last_change_date = Keyword(index=False)

    class Index:
        name = 'persons'
        settings = index_settings

    class Meta:
        dynamic = MetaField('strict')
