from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer
from sqlalchemy.schema import CheckConstraint

from app.core.db import Base


class BaseModel(Base):
    __abstract__ = True

    full_amount = Column(Integer)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime)

    def __repr__(self) -> str:
        return (
            f'id={self.id} - full_amount={self.full_amount} - '
            f'invested_amount={self.invested_amount} - '
            f'fully_invested={self.fully_invested} - '
            f'create_date={self.create_date} - close_date={self.close_date}'
        )

    __table_args__ = (
        CheckConstraint('full_amount > 0', name='full_amount_positive'),
    )
