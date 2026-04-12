from django.urls import path

from projects.views import open_project_page, open_project_members_page, open_project_settings, api_get_project_domains, \
    api_get_project_requirements, api_add_project_domains, api_delete_project_domains

app_name = 'projects'

urlpatterns = [
    path("project-page/<str:name>/",open_project_page,name="project-page"),
    path("project-page/<str:name>/project-members/",open_project_members_page,name="project-members"),
    path("project-page/<str:name>/settings/",open_project_settings,name="project-settings"),
    path("api-get-project-domains",api_get_project_domains,name="get-project-domains"),
    path("settings/<str:name>/api-project-domains", api_get_project_domains, name="get-domains-from-settings"),
    path("<str:name>/api-get-project-requirements",api_get_project_requirements,name="get-requirements"),
    path("settings/<str:name>/api-project-domains",api_get_project_requirements,name="get-requirements-from-settings"),
    path("settings/<str:name>/api-add-domains",api_add_project_domains,name="add-domains-to-project"),
    path("settings/<str:name>/api-remove-domains",api_delete_project_domains,name="add-domains-to-project")
]


