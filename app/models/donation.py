from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.base import BaseModel


class Donation(BaseModel):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)

    def __repr__(self) -> str:
        return super().__repr__() + f' user_id={self.user_id} comment="{self.comment[:15]}"'
