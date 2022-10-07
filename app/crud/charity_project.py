from typing import Optional

from sqlalchemy import select
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
    ):
        projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested
            )
        )
        return projects.scalars().all()


charity_project_crud = CRUDCharityProject(CharityProject)
