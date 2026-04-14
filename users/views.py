import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from projects.models import Project
from .models import User, UserProfileSection, UserTechnicalSkillSection, UserTechnicalSkill, UserRequest
from .search import SearchManager, SearchFilterData


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
            data = SearchFilterData(user_id=request.user.id,query=query,search_type='ALL',sort_by_date=False,sort_by_relevance=False)
            manager = SearchManager()
            manager.execute_search(data)
            results = manager.get_results_from_search()
            return JsonResponse({
                'status':'success',
                'results':results
            })
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(str(e))
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
        "user_posts":[],
    }
    if request.user.username == username:
        profile_stats["profile_sections"] = (UserProfileSection.
                                        objects.
                                        get_user_profile_sections(user,includehidden=True))
    else:
        profile_stats["profile_sections"] = (UserProfileSection.
                                             objects.
                                             get_user_profile_sections(user, includehidden=False))
    profile_stats["techstack_category"] = UserTechnicalSkillSection.objects.get_user_techstack(user)
    profile_stats["profile_projects"] = Project.objects.get_user_projects(user)
    requested = False
    try:
        friendship_request = UserRequest.objects.find_request(request.user, user)
        if friendship_request is not None:
            requested = True
    except Exception as e:
            requested = False
    context = {
        "username":user.username,
        "email":user.email,
        "id":user.id,
        "user":user,
        "profile_sections":profile_stats["profile_sections"],
        "techstack_category":profile_stats["techstack_category"],
        "user_projects":profile_stats["profile_projects"],
        "user_posts":profile_stats["user_posts"],
        "is_owner":request.user.username == username,
        "requested_friendship":requested
    }
    return render(request, "html/profile.html", context)
@login_required
def inbox_page(request):
    pass
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
@require_http_methods(["GET","POST"])
def create_project(request):
    if request.method == 'GET':
        return render(request,'html/create_project.html',{"user_id":request.user.id})
    elif request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        user_id = request.user.id
        Project.objects.create_project(user_id,name, description)
        return acces_profile(request,request.user.username)
@require_http_methods(["POST"])
@csrf_exempt
def api_add_skill(request):
    name = request.POST.get('name')
    section_id = request.POST.get('section_id')
    print(f"name={name}, section_id={section_id}")

    if not name or not section_id:
        return JsonResponse({'status': 'error', 'message': 'Date lipsă'}, status=400)

    success = UserTechnicalSkill.objects.add_user_skill(name=name, section_id=section_id)
    return JsonResponse({'status': 'success' if success else 'error'})
@require_http_methods(["DELETE"])
@csrf_exempt
def api_delete_skill(request,skill_id):
    try:
        skill = UserTechnicalSkill.objects.get(id=skill_id)
        success = UserTechnicalSkill.objects.remove_user_skill(skill)
        return JsonResponse({'status': 'success'})
    except UserTechnicalSkill.DoesNotExist:
        return JsonResponse({'status':'error','message':'Skill not found'},status=404)
@require_http_methods(["POST"])
@login_required
def api_send_friend_request(request,receiver):
    try:
        # get() aruncă User.DoesNotExist dacă nu găsește, deci nu e nevoie de "is None"
        user = User.objects.get(id=receiver)
        if user == request.user:
            return JsonResponse({'status': 'error', 'message': "Cannot send request to self"}, status=400)
        # Trimiți obiectul request.user, nu request.user.id
        sent = UserRequest.objects.send_friend_request(request.user, user)
        if sent is None:
            return JsonResponse({'status': 'error', 'message': 'Request already exists or failed'}, status=400)
        # Aici aveai status 404 pentru "succes", l-am schimbat in 200
        return JsonResponse({'status': 'succes', 'code': 200})
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
    except Exception as e:
        print(f"Eroare API: {str(e)}")
        # Acum view-ul returnează un JSON chiar și când crapă ceva, evitând eroarea 500 în browser
        return JsonResponse({'status': 'error', 'message': 'Internal Server Error'}, status=500)
@require_http_methods(["POST"])
@login_required
def api_accept_friend_request(request,sender):
    try:
        # get() aruncă User.DoesNotExist dacă nu găsește, deci nu e nevoie de "is None"
        user = User.objects.get(id=sender)
        if user == request.user:
            return JsonResponse({'status': 'error', 'message': "Cannot accept request from self"}, status=400)
        # Trimiți obiectul request.user, nu request.user.id
        friend_request = UserRequest.objects.find_request(user,request.user)
        if friend_request is None:
            return  JsonResponse({'status':'error','message':'No request received from certain user'},status=404)
        if friend_request.first().status != 'pending':
            return JsonResponse({'status': 'error', 'message': 'Request has already been handled'}, status=403)
        sent = UserRequest.objects.accept_request(friend_request.first())
        if sent is None:
            return JsonResponse({'status': 'error', 'message': 'Request already exists or failed'}, status=400)
        # Aici aveai status 404 pentru "succes", l-am schimbat in 200
        return JsonResponse({'status': 'succes', 'code': 200})
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
    except Exception as e:
        print(f"Eroare API: {str(e)}")
        # Acum view-ul returnează un JSON chiar și când crapă ceva, evitând eroarea 500 în browser
        return JsonResponse({'status': 'error', 'message': 'Internal Server Error'}, status=500)
@login_required
def connections_page(request):
    try:
        requests = UserRequest.objects.get_user_requests(request.user)
        return render(request, 'html/connections.html', {'context': {'user': request.user,
                'requests': requests}
                })
    except Exception:
        return render(request, 'html/connections.html', {'context': {'user': request.user,
                                                                     'requests': []}
                                                         })