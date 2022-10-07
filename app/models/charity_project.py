from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.schema import CheckConstraint

from app.models.base import BaseModel


class CharityProject(BaseModel):

    @declared_attr
    def __table_args__(cls):
        return (
            *super().__table_args__,
            CheckConstraint('length(name) > 0', name='length_name'),
            CheckConstraint('length(description) > 0', name='length_description')
        )

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)

    def __repr__(self) -> str:
        return (
            super().__repr__() +
            f' name={self.name[:15]} description={self.description[:15]}'
        )
