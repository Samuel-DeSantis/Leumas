"""Root Django Ninja API.

Session-authenticated (the same login used by the HTMX UI); CSRF is
enforced for unsafe methods so browser clients must send the standard
Django CSRF header/cookie.
"""

from ninja import NinjaAPI
from ninja.security import django_auth

from apps.electrical.api import router as electrical_router
from apps.equipment.api import router as equipment_router
from apps.organizations.api import router as organizations_router
from apps.projects.api import router as projects_router

api = NinjaAPI(title="PV Engineering Platform API", version="1.0.0", auth=django_auth)

api.add_router("/organizations/", organizations_router)
api.add_router("/organizations/", projects_router)
api.add_router("/organizations/", equipment_router)
api.add_router("/organizations/", electrical_router)
