import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from projects.models import Project, UserProjectRole


@login_required
def create_project(request):
    if request.method == 'POST':

        open_project_page(request)
    else:
        JsonResponse({'status': 'error',
                      'code' : 404
                      })
@login_required
def open_project_page(request,name):
    role_admin = UserProjectRole.objects
    user = request.user
    project = Project.objects.filter(name=name).first()
    if project is None:
        return JsonResponse({
            'status':'failed',
            'code':404
        })
    staff = UserProjectRole.objects.get_all_users_in_project(project)
    roles = staff.keys()
    context_data = {
        'role': 'visitor',
        'user_id': user.id,
        'user_username': user.username,
        'project_name': project.name,
        'project_id': project.id,
        'staff':staff,
        'roles':roles
    }
    if role_admin.is_user_in_project(project,user):
        context_data['role'] = role_admin.get_user_role_in_project(project,user)
    return render(request,'html/project_page.html',{'stats':context_data}
    )