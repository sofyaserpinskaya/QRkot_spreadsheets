from datetime import datetime
from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation
from app.crud.base import CRUDBase


async def set_fully_invested(
    object: Union[Donation, CharityProject],
) -> None:
    object.fully_invested = True
    object.close_date = datetime.now()


async def project_invest(
    target: Union[Donation, CharityProject],
    session: AsyncSession
):
    sources = await CRUDBase.get_not_invested(
        CharityProject if isinstance(target, Donation) else Donation,
        session
    )
    if not sources:
        return None
    result = []
    for source in sources:
        result.append(source)
        amount = min(
            source.full_amount - source.invested_amount,
            target.full_amount - target.invested_amount
        )
        for item in (target, source):
            item.invested_amount += amount
            if item.full_amount == item.invested_amount:
                await set_fully_invested(item)
        if target.fully_invested:
            break
    return result
