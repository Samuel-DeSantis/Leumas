import uuid

from ninja import Schema


class OrganizationOut(Schema):
    id: uuid.UUID
    name: str
    slug: str


class OrganizationIn(Schema):
    name: str


class MembershipOut(Schema):
    id: uuid.UUID
    user_email: str
    role: str

    @staticmethod
    def resolve_user_email(obj):
        return obj.user.email
