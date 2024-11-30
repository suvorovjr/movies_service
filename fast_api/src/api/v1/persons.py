from http import HTTPStatus
import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from src.models.person import Person
from src.services.persons import PersonService, get_person_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=list[Person])
async def person_list(
    person_service: PersonService = Depends(get_person_service),
    sort: str = "full_name",
    page_size: int = Query(10, gt=0, le=100),
    page: int = Query(1, ge=1),
) -> list[Person] | None:

    persons = await person_service.get_persons_by_query(
        sort=sort, page_size=page_size, page=page
    )
    if not persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Ошибка при получении фильмов"
        )
    return persons


@router.get("/{person_id}", response_model=Person)
async def person_details():
    pass


@router.get("/search/")
async def person_search():
    pass


@router.get("/{person_id}/films/")
async def films_by_person():
    pass
