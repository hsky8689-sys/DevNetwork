from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.shortcuts import redirect
from users.views import login_page, signup_page, acces_profile

app_name = 'users'

def redirect_to_login(request):
    return redirect('user_login')
urlpatterns = [
    path("signup/",signup_page),
    path("profile/<str:username>/",acces_profile,name="profile-path"),
    path("logout/",auth_views.LogoutView.as_view(
    template_name="html/logout.html",next_page="login.html")
    ,name="logout")
]