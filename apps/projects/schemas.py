import uuid
from decimal import Decimal

from ninja import Schema


class ProjectOut(Schema):
    id: uuid.UUID
    name: str
    description: str
    location: str
    ac_nameplate_capacity_kw: Decimal | None = None


class ProjectIn(Schema):
    name: str
    description: str = ""
    location: str = ""
    ac_nameplate_capacity_kw: Decimal | None = None
