from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.shortcuts import redirect
from users.views import login_page, signup_page, acces_profile, api_add_skill, api_delete_skill, search_page, \
    search_api, create_project

app_name = 'users'

def redirect_to_login(request):
    return redirect('user_login')
urlpatterns = [
    path("signup/",signup_page),
    path("profile/<str:username>/",acces_profile,name="profile-path"),
    path("logout/",auth_views.LogoutView.as_view(
    template_name="html/logout.html",next_page="login.html")
    ,name="logout"),
    path('api/add-skill/',api_add_skill,name='api_add_skill'),
    path('search/', search_page, name='search_page'),
    path('search/api/', search_api, name='search_api'),
    path('api/delete-skill/',api_delete_skill,name='api_delete_skill'),
    path('create-new-project/',create_project,name='create_project')
]