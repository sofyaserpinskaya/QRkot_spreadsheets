from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


FULL_AMOUNT_ERROR = (
    'Нельзя установить требуемую сумму меньше уже вложенной. '
    'Вложенная в проект {project} сумма - {amount}'
)
NAME_EXISTS_ERROR = 'Проект с таким именем уже существует!'
PROJECT_CLOSED_ERROR = 'Закрытый проект нельзя редактировать!'
PROJECT_DELETE_ERROR = 'В проект были внесены средства, не подлежит удалению!'
PROJECT_DOES_NOT_EXIST_ERROR = 'Проект {} не найден.'


async def check_name_duplicate(
        project_name: str,
        session: AsyncSession,
) -> None:
    project = await charity_project_crud.get_project_by_name(
        project_name, session
    )
    if project is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=NAME_EXISTS_ERROR,
        )


async def check_charity_project_before_update(
    project_id: int,
    session: AsyncSession,
    full_amount: Optional[int] = None
) -> CharityProject:
    charity_project = await charity_project_crud.get(
        project_id, session
    )
    if charity_project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=PROJECT_DOES_NOT_EXIST_ERROR.format(charity_project.name)
        )
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=PROJECT_CLOSED_ERROR
        )
    if full_amount:
        if full_amount < charity_project.invested_amount:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail=FULL_AMOUNT_ERROR.format(
                    project=charity_project.name,
                    amount=charity_project.invested_amount
                )
            )
    return charity_project


async def check_charity_project_before_delete(
    project_id: int,
    session: AsyncSession,
) -> CharityProject:
    charity_project = await charity_project_crud.get(
        project_id, session
    )
    if charity_project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=PROJECT_DOES_NOT_EXIST_ERROR.format(charity_project.name)
        )
    if charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=PROJECT_DELETE_ERROR
        )
    return charity_project
