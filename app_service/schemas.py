from typing import List
from pydantic import BaseModel

from .models.models import ProbaTable


class Proba(BaseModel):
    pass


class ProbaCreate(Proba):
    name: str

    class Config:
        orm_mode = True


# class ProbaGet(Proba):
#     proba: List[ProbaTable]
#
#     class Config:
#         orm_mode = True

