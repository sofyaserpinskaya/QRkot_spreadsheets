from datetime import datetime
from typing import List

from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import CharityProjectDB
from app.services.google_api import (
    set_user_permissions, spreadsheets_create, spreadsheets_update_value
)


FORMAT = "%Y/%m/%d %H:%M:%S"


router = APIRouter()


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    dependencies=[Depends(current_superuser)],
)
async def get_report(
        session: AsyncSession = Depends(get_async_session),
        wrapper_services: Aiogoogle = Depends(get_service)

):
    """Только для суперюзеров."""
    projects = await charity_project_crud.get_projects_by_completion_rate(
        session
    )
    now_date_time = datetime.now().strftime(FORMAT)
    spreadsheet_id = await spreadsheets_create(wrapper_services, now_date_time)
    await set_user_permissions(spreadsheet_id, wrapper_services)
    await spreadsheets_update_value(
        spreadsheet_id, projects, wrapper_services, now_date_time
    )
    return projects
