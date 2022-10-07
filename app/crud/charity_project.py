from datetime import datetime
from typing import Dict, List, Optional, Union

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):

    @staticmethod
    async def get_project_by_name(
        project_name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        return project_id.scalars().first()

    @staticmethod
    async def get_projects_by_completion_rate(
        session: AsyncSession,
    ) -> List[Dict[str, Union[str, datetime]]]:
        projects = await session.execute(
            select([
                CharityProject.name,
                CharityProject.create_date,
                CharityProject.close_date,
                CharityProject.description
            ]).where(
                CharityProject.fully_invested
            ).group_by(
                func.julianday(CharityProject.close_date) -
                func.julianday(CharityProject.create_date)
            )
        )
        return projects.all()


charity_project_crud = CRUDCharityProject(CharityProject)
