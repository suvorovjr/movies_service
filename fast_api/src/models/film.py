from pydantic import BaseModel


class Person(BaseModel):
    id: str
    name: str


class Film(BaseModel):
    id: str
    imdb_rating: float
    genres: list[str]
    title: str
    description: str | None = None
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]
    directors: list[Person] | None
    actors: list[Person]
    writers: list[Person]


class ResponseFilm(BaseModel):
    id: str
    imdb_rating: float
    genres: list[str]
    title: str
    description: str | None = None
    directors: list[Person]
    actors: list[Person]
    writers: list[Person]
