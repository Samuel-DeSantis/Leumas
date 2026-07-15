def current_organization(request):
    return {"current_organization": getattr(request, "organization", None)}
