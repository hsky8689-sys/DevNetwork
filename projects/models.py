from collections import defaultdict

from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.db.models import Q

from users.models import User

# Create your models here.
class ProjectManager(BaseUserManager):
    def makeNewOwner(self,project):
        """

        :param project:
        :return:
        """
        if User.objects.get(project.owner_id) is not None:
            raise ValueError("The owner didnt delete his account")
    def create_project(self,user,project):
        """
        Creates a project and automatically sets the given user as owner
        :param user: The future project creator and owner
        :return:
        """
        return True
    def delete_project(self,project):
        """
        Deletes a project from the database
        :param project:
        :return:
        """
        Project.objects.get(id=project.id).delete()
        return Project.objects.filter(id=project.id).count() == 0

    def get_user_projects(self,user):
        """
        Returns all the projects that an specified user participated in
        :param project:
        :return:
        """
        return self.filter(id__in=UserProjectRole.objects.filter(user_id=user.id)).values_list('id',flat=True)

    def get_all_users_in_project(self,project):
        """
        Returns the whole users that ever participated/are participating now in a project
        :param project:
        :return: A dictionary with the participants grouped by the roles in the given project
        """
        roles = UserProjectRole.objects.filter(project=project).select_related('user')
        users_by_role = defaultdict(list)
        for role_obj in roles:
            users_by_role[role_obj.role].append(role_obj.user)
        return dict(users_by_role)

class Project(models.Model):
    owner=models.ForeignKey(User,on_delete=ProjectManager.makeNewOwner)
    objects = ProjectManager()
    class Meta:
        db_table = 'projects'

class ProjectTask(models.Model):
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    name = models.CharField(max_length=100,blank=False)
    description = models.CharField(max_length=300,blank=False)
    start_date = models.DateField()
    end_date = models.DateField(blank=True)
    class Meta:
        db_table = 'projects_tasks'

class UserRoleManager(BaseUserManager):
    def is_user_in_project(self, project, user):
        """
        Checks if an user is already in a project
        :param project:
        :param user:
        :return:
        """
        return UserProjectRole.objects.filter(Q(project_id=project.id) | Q(user_id=user.id)).count() == 1

class UserProjectRole(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    role = models.CharField(default='Developer')
    class Meta:
        db_table = 'project_roles'

class ProjectTaskParticipation(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    task = models.ForeignKey(ProjectTask,on_delete=models.CASCADE)
    class Meta:
        db_table = 'project_task_participations'
