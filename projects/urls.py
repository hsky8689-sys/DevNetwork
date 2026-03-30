from django.urls import path

from projects.views import open_project_page, open_project_members_page,open_project_settings

app_name = 'projects'

urlpatterns = [
    path("project-page/<str:name>/",open_project_page,name="project-page"),
    path("project-page/<str:name>/project-members/",open_project_members_page,name="project-members"),
    path("project-page/<str:name>/settings/",open_project_settings,name="project-settings"),
]


