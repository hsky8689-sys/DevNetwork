import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from projects.models import Project
from .models import User, UserProfileSection, UserTechnicalSkillSection,UserTechnicalSkill

# Create your views here.
@login_required
def search_page(request):
    return render(request, 'html/search.html', {'user_id': request.user.id})
@login_required
@csrf_exempt
def search_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query','').lower()

            people = User.objects.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query)
            ).values('id','username','email')[:10]
            print(list(people))
            return JsonResponse({
                'status':'success',
                'results':{'people':list(people)}
            })
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
def signup_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        birthday = request.POST['birthday']
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                birthday=birthday
            )
            login(request,user)
            messages.success(request,f'Bun venit, {user.username}!')
            return redirect('user_profile',username=username)
        except Exception as e:
            messages.error(request,f'Error :{str(e)}')
        messages.success(request, 'Cont creat!')
        return redirect('user_login')

    return render(request, 'html/signup.html')
@login_required
def acces_profile(request,username):
    user = get_object_or_404(User,username=username)
    profile_stats = {
        "profile_sections":[],
        "teckstack_category":{},
        "profile_projects":[],
        "user_posts":[]
    }
    if request.user.username == username:
        profile_stats["profile_sections"] = UserProfileSection.objects.get_user_profile_sections(request.user,includehidden=True)
    else:
        profile_stats["profile_sections"] = UserProfileSection.objects.get_user_profile_sections(user)
    profile_stats["techstack_category"] = UserTechnicalSkillSection.objects.get_user_techstack(user)
    profile_stats["profile_projects"] = Project.objects.get_user_projects(user)
    context = {
        "username":user.username,
        "email":user.email,
        "user":user,
        "profile_sections":profile_stats["profile_sections"],
        "techstack_category":profile_stats["techstack_category"],
        "user_projects":profile_stats["profile_projects"],
        "user_posts":profile_stats["user_posts"],
        "is_owner":request.user.username == username
    }
    return render(request, "html/profile.html", context)
def login_page(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            logout(request)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user:
            login(request, user)
            return redirect('users:profile-path', username=username)
        else:
            messages.error(request,'Date incorecte')
            return redirect('user_login')
    else:
        if request.user.is_authenticated:
            logout(request)
        return render(request, "html/login.html")
@require_http_methods(["POST"])
@csrf_exempt
def api_add_skill(request):
    name = request.POST.get('name')
    section_id = request.POST.get('section_id')

    success = UserTechnicalSkill.objects.add_user_skill(name=name,section_id=section_id)
    return JsonResponse({'status':'success' if success else 'error',
                         'message':'Skill was added' if success else 'Error!'
    })
@require_http_methods(["DELETE"])
@csrf_exempt
def api_delete_skill(request,skill_id):
    try:
        skill = UserTechnicalSkill.objects.get(id=skill_id)
        success = UserTechnicalSkill.objects.remove_user_skill(skill)
        return JsonResponse({'status': 'success'})
    except UserTechnicalSkill.DoesNotExist:
        return JsonResponse({'status':'error','message':'Skill not found'},status=404)