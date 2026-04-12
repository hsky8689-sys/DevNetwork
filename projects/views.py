import json

import django.db
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import users.views
from projects.models import Project, UserProjectRole, ProjectDomain,ProjectSkillRequirement,ProjectRequirementSection


@login_required
def create_project(request):
    if request.method == 'POST':

        users.views.acces_profile(request,request.user.username)
    else:
        return JsonResponse({'status': 'error',
                      'code' : 404
                      })
@login_required
def open_project_page(request,name):
    project = Project.objects.filter(name=name).first()
    if not project:
        return JsonResponse({'status': 'failed', 'code': 404})
    staff = UserProjectRole.objects.get_all_users_in_project(project)
    user_role = UserProjectRole.objects.get_user_role_in_project(project, request.user)
    visitor_permissions = UserProjectRole.objects.get_role_permissions(user_role,project)
    project_domains = ProjectDomain.objects.get_project_domains(project)
    context_data = {
        'role': user_role,
        'user_id': request.user.id,
        'user_username': request.user.username,
        'project_name': project.name,
        'project_id': project.id,
        'staff': staff,
        'roles': list(staff.keys()),
        'domains':list(project_domains),
        'description':project.description,
        'visitor_permissions':visitor_permissions
    }
    return render(request, 'html/project_page.html', {'stats': context_data})
@login_required
def open_project_members_page(request,name):
    project = Project.objects.filter(name=name).first()
    result = UserProjectRole.objects.get_all_users_in_project(project)
    stats = {'members': result, 'project_name': project.name}
    return render(request, 'html/project_members_page.html', {'stats': stats})

@login_required
@csrf_exempt
def open_project_settings(request, name):
    project = get_object_or_404(Project, name=name)
    user_role = UserProjectRole.objects.get_user_role_in_project(project, request.user)

    context_data = {
        'project_name': project.name,
        'project_id': project.id,
        'role': user_role,
        'user_username': request.user.username,
    }
    return render(request, 'html/project_settings_page.html', {'stats': context_data})
@login_required
def send_project_join_request(request,project):
    pass
@require_http_methods(["GET"])
@csrf_exempt
def api_get_project_domains(request,name):
    try:
        project = get_object_or_404(Project,name=name)
        domains = ProjectDomain.objects.filter(project_id=project.id)
        return JsonResponse({'status':'success','domains':list(domains.values())})
    except django.db.DatabaseError:
        return JsonResponse({'status': 'error', 'code': 500})
@require_http_methods(["POST"])
@csrf_exempt
def api_add_project_domains(request,name):
    try:
        if request.method == 'POST':
            project = get_object_or_404(Project,name=name)
            role = UserProjectRole.objects.get_user_role_in_project(project,request.user)
            if UserProjectRole.objects.get_role_permissions(role,project)['can_change_project_settings']:
                data = json.loads(request.body)
                domains = data.get('newDomains',[])
                succes = ProjectDomain.objects.add_domains_to_project(project,domains)
                return JsonResponse({'status':'succes' if len(succes) == len(domains) else 'error',
                             'code':200 if len(succes) == len(domains) else 404
                })
            else:
                return JsonResponse({'status':'Unauthorized access','code':403})
    except Exception as e:
        print(str(e))
    except django.db.DatabaseError:
        return JsonResponse({'status': 'error', 'code': 500})
@require_http_methods(["POST"])
@csrf_exempt
def api_delete_project_domains(request,name):
    try:
        if request.method == 'POST':
            project = get_object_or_404(Project, name=name)
            role = UserProjectRole.objects.get_user_role_in_project(project, request.user)
            if UserProjectRole.objects.get_role_permissions(role, project)['can_change_project_settings']:
                data = json.loads(request.body)
                domains = data.get('removedDomains', [])
                succes = ProjectDomain.objects.remove_domains_from_project(project, domains)
                return JsonResponse({'status': 'succes' if len(succes) == len(domains) else 'error',
                                     'code': 200 if len(succes) == len(domains) else 404
                                     })
            else:
                return JsonResponse({'status': 'Unauthorized access', 'code': 403})
    except Exception as e:
        print(str(e))
    except django.db.DatabaseError:
        return JsonResponse({'status': 'error', 'code': 500})
@require_http_methods(["GET"])
@csrf_exempt
def api_get_project_requirements(request,name):
    try:
        project = get_object_or_404(Project,name=name)
        succes = ProjectSkillRequirement.objects.get_requirements_grouped_by_sections(project)
        return JsonResponse({'status':'succes','requirements':succes})
    except Exception as e:
        print(str(e))
    except django.db.DatabaseError:
        return JsonResponse({'status': 'error', 'code': 404})