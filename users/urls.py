from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import path

from users.views import signup_page, acces_profile, api_add_skill, api_delete_skill, search_page, \
    search_api, create_project, api_send_friend_request, connections_page, api_accept_friend_request

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
    path('create-new-project/',create_project,name='create_project'),
    path('<int:receiver>/send-friend-request/',api_send_friend_request,name='send_friend_request'),
    path('<int:sender>/accept-friend-request/',api_accept_friend_request,name='send_friend_request'),
    path('connections-page/',connections_page,name='view_connections')
]