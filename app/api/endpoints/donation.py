from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.crud.donation import donation_crud
from app.models import Donation, User
from app.services.investment import project_invest
from app.schemas.donation import DonationCreate, DonationDB, DonationGetAll


router = APIRouter()


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True
)
async def create_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
) -> Donation:
    """
    Сделать пожертвование.
    """
    donation = await donation_crud.create(donation, session, user)
    invested = await project_invest(
        donation,
        session
    )
    if invested:
        session.add_all([*invested, donation])
        await session.commit()
        await session.refresh(donation)
    return donation


@router.get(
    '/',
    response_model=List[DonationGetAll],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session)
) -> List[Donation]:
    """
    Только для суперюзеров.

    Возвращает список всех пожертвований.
    """
    return await donation_crud.get_multi(session)


@router.get(
    '/my',
    response_model=List[DonationDB],
    response_model_exclude_none=True
)
async def get_user_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
) -> Donation:
    """
    Вернуть список пожертвований пользователя, выполняющего запрос.
    """
    return await donation_crud.get_by_user(session, user)
