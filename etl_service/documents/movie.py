from elasticsearch_dsl import (
    Document,
    Float,
    InnerDoc,
    Keyword,
    MetaField,
    Nested,
    Text,
)

from .index_settings import index_settings


class Director(InnerDoc):
    id = Keyword()
    name = Text(analyzer='ru_en')

    class Meta:
        dynamic = MetaField('strict')


class Actor(InnerDoc):
    id = Keyword()
    name = Text(analyzer='ru_en')

    class Meta:
        dynamic = MetaField('strict')


class Writer(InnerDoc):
    id = Keyword()
    name = Text(analyzer='ru_en')

    class Meta:
        dynamic = MetaField('strict')


class Movie(Document):
    id = Keyword()
    imdb_rating = Float()
    genres = Keyword()
    title = Text(analyzer='ru_en', fields={'raw': Keyword()})
    description = Text(analyzer='ru_en')
    directors_names = Text(analyzer='ru_en')
    actors_names = Text(analyzer='ru_en')
    writers_names = Text(analyzer='ru_en')
    directors = Nested(Director)
    actors = Nested(Actor)
    writers = Nested(Writer)
    last_change_date = Keyword(index=False)

    class Index:
        name = 'movies'
        settings = index_settings

    class Meta:
        dynamic = MetaField('strict')
