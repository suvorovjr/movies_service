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


class Genre(Document):
    id = Keyword()
    name = Text(analyzer='ru_en', fields={'raw': Keyword()})

    class Index:
        name = 'genres'
        settings = index_settings

    class Meta:
        dynamic = MetaField('strict')


indexes = [
    Genre,
    Person,
    Movie
]