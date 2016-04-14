from django.conf import settings
from mrvapi.models import Project, ProjectPermissions

def add_project(request):
    try:
        project_id = request.session.get('project_id')
        project = Project.objects.get(pk=project_id)
    except:
        project = None

    return {'project':project}

def add_permission(request):
    try:
        project_id = request.session.get('project_id')
        project = Project.objects.get(pk=project_id)
    except:
        project = None

    perm = None
    if project:
        perm = ProjectPermissions.objects.get(project=project, user=request.user)

    return {'perm': perm}