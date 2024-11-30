from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, Query

from src.models.film import ResponseFilm
from src.services.film import FilmService, get_film_service

router = APIRouter()


def create_response_films(films: list) -> list[ResponseFilm]:
    """Вспомогательная функция для преобразования списка фильмов в ResponseFilm"""
    return [ResponseFilm(**film.dict()) for film in films]


def handle_no_films_error(films: list, query_params: dict):
    """Обрабатывает ошибку, если фильмы не найдены и добавляет информацию о запросе"""
    if not films:
        query_info = ", ".join(f"{key}: {value}" for key, value in query_params.items())
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"No films found for query: {query_info}",
        )


@router.get("/", response_model=list[ResponseFilm])
async def film_list(
    sort: str = Query(
        default="-imdb_rating", enum=["imdb_rating", "-imdb_rating"], alias="sort"
    ),
    page_size: int = Query(default=50, ge=1, le=50, alias="page_size"),
    page: int = Query(default=1, ge=1),
    film_service: FilmService = Depends(get_film_service),
) -> list[ResponseFilm]:
    """Получаем список фильмов с кэшированием"""
    films = await film_service.get_film_list(sort=sort, page_size=page_size, page=page)
    handle_no_films_error(films, {"sort": sort, "page_size": page_size, "page": page})
    return create_response_films(films)


@router.get("/{film_id}", response_model=ResponseFilm)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> ResponseFilm:
    """Получаем подробности фильма по ID"""
    
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Film not found")
    return ResponseFilm(**film.dict())


@router.get("/search/", response_model=list[ResponseFilm])
async def film_search(
    query: str = Query(..., alias="query"),
    sort: str = Query(
        default="-imdb_rating", enum=["imdb_rating", "-imdb_rating"], alias="sort"
    ),
    page_size: int = Query(default=50, gt=1, le=50, alias="page_size"),
    page: int = Query(default=1, ge=1, alias="page"),
    film_service: FilmService = Depends(get_film_service),
) -> list[ResponseFilm]:
    """Поиск фильмов по запросу"""

    films = await film_service.get_films_by_query(
        query=query, sort=sort, page_size=page_size, page=page
    )
    handle_no_films_error(
        films, {"query": query, "sort": sort, "page_size": page_size, "page": page}
    )
    return create_response_films(films)
