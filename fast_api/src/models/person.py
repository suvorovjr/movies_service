from .mixins import EntityBase
from pydantic import BaseModel
from typing import List, Optional



class ShortFilm(BaseModel):
    id: str
    title: str
    imdb_rating: float


class FilmRole(BaseModel):
    id: str
    roles: List[str]


class Person(BaseModel):
    id: str
    full_name: str
    films: List[FilmRole]


class Actor(EntityBase):
    pass


class Writer(EntityBase):
    pass


class Director(EntityBase):
    pass


class Genre(EntityBase):
    pass
