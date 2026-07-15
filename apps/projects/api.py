from django.shortcuts import get_object_or_404
from ninja import Router

from apps.organizations.api_auth import get_org_and_membership

from .models import Project
from .schemas import ProjectIn, ProjectOut

router = Router(tags=["projects"])


@router.get("/{org_slug}/projects/", response=list[ProjectOut])
def list_projects(request, org_slug: str):
    organization, _ = get_org_and_membership(request, org_slug)
    return Project.objects.filter(organization=organization).order_by("-created_at")


@router.post("/{org_slug}/projects/", response=ProjectOut)
def create_project(request, org_slug: str, payload: ProjectIn):
    organization, _ = get_org_and_membership(request, org_slug, required_edit=True)
    return Project.objects.create(organization=organization, created_by=request.user, **payload.dict())


@router.get("/{org_slug}/projects/{project_id}/", response=ProjectOut)
def get_project(request, org_slug: str, project_id: str):
    organization, _ = get_org_and_membership(request, org_slug)
    return get_object_or_404(Project, pk=project_id, organization=organization)


@router.put("/{org_slug}/projects/{project_id}/", response=ProjectOut)
def update_project(request, org_slug: str, project_id: str, payload: ProjectIn):
    organization, _ = get_org_and_membership(request, org_slug, required_edit=True)
    project = get_object_or_404(Project, pk=project_id, organization=organization)
    for field, value in payload.dict().items():
        setattr(project, field, value)
    project.save()
    return project


@router.delete("/{org_slug}/projects/{project_id}/")
def delete_project(request, org_slug: str, project_id: str):
    organization, _ = get_org_and_membership(request, org_slug, required_edit=True)
    project = get_object_or_404(Project, pk=project_id, organization=organization)
    project.delete()
    return {"success": True}
