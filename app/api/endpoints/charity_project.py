from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_charity_project_before_delete, check_charity_project_before_update,
    check_name_duplicate
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.models import CharityProject
from app.services.investment import project_invest
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)


router = APIRouter()


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session),
) -> List[CharityProject]:
    """
    Возвращает список всех проектов.
    """
    return await charity_project_crud.get_multi(session)


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
    charity_project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
) -> CharityProject:
    """
    Только для суперюзеров.

    Создаёт благотворительный проект.
    """
    await check_name_duplicate(charity_project.name, session)
    charity_project = await charity_project_crud.create(charity_project, session)
    invested = await project_invest(
        charity_project,
        session
    )
    if invested:
        session.add_all([*invested, charity_project])
        await session.commit()
        await session.refresh(charity_project)
    return charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> CharityProject:
    """
    Только для суперюзеров.

    Удаляет проект. Нельзя удалить проект,
    в который уже были инвестированы средства, его можно только закрыть.
    """
    return await charity_project_crud.remove(
        await check_charity_project_before_delete(project_id, session),
        session
    )


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> CharityProject:
    """
    Только для суперюзеров.

    Закрытый проект нельзя редактировать;
    нельзя установить требуемую сумму меньше уже вложенной.
    """
    if obj_in.full_amount is not None:
        charity_project = await check_charity_project_before_update(
            project_id, session, obj_in.full_amount
        )
    else:
        charity_project = await check_charity_project_before_update(
            project_id, session
        )
    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)
    charity_project = await charity_project_crud.update(charity_project, obj_in, session)
    invested = await project_invest(
        charity_project,
        session
    )
    if invested:
        session.add_all([*invested, charity_project])
        await session.commit()
        await session.refresh(charity_project)
    return charity_project
