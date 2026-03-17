from collections import defaultdict

import django.db
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.decorators import login_required
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
    def create_project(self,user,name,description):
        """
        Creates a project and automatically sets the given user as owner
        :param user: The future project creator and owner
        :return:
        """
        proj = self.create(owner_id=user,name=name,description=description)
        UserProjectRole.objects.create(role='owner',project_id=proj.id,user_id=user)

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
        #return self.filter(id__in=UserProjectRole.objects.filter(user_id=user.id)).values_list('id',flat=True)

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
    name=models.CharField(max_length=100,blank=False,null=False,default='New project')
    description=models.CharField(max_length=5000,blank=False,null=False,default='Project description')
    objects = ProjectManager()
    class Meta:
        db_table = 'projects'

class ProjectDomain(models.Model):
    project=models.ForeignKey(Project,on_delete=models.CASCADE)
    domain=models.CharField(max_length=100,blank=False,null=False,default='new domain')
    class Meta:
        db_table = 'project_domains'

class ProjectTask(models.Model):
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    name = models.CharField(max_length=100,default='New task',blank=True)
    description = models.CharField(max_length=300,default='Describe the task..',blank=True)
    start_date = models.DateField(default='1000-10-10')
    end_date = models.DateField(default='3000-10-10')
    class Meta:
        db_table = 'projects_tasks'

class UserRoleValidator():
    def is_operation_permitted(self,project,role_assignator,user,new_role):
        """

        :param role_assignator:
        :param user:
        :param new_role:
        :return:
        """
        _project = Project.objects.get(id=project)
        if _project is None:
            raise ValueError("Project not found")
        _role_assigner = User.objects.get(id=role_assignator)
        if user is None:
            raise ValueError("Role assignator not found")
        _user = User.objects.get(id=user)
        if _user is None:
            raise ValueError("User not found")
        if _project.owner_id == role_assignator:
            return True
        is_assigner = UserRoleManager.is_user_in_project(_project,_role_assigner)
        is_user = UserRoleManager.is_user_in_project(_project, _user)
        if not is_assigner:
            raise ValueError("Assigner not found")
        if not is_user:
            raise ValueError("User not found")
        #permission checking TODO
        return True

class UserRoleManager(BaseUserManager):
    def is_user_in_project(self, project, user):
        """
        Checks if an user is already in a project
        :param project:
        :param user:
        :return:
        """
        #return UserProjectRole.objects.filter(Q(project_id=project.id) | Q(user_id=user.id)).count() == 1
    @login_required
    def give_role_to_user(self,project:int,role_assigner:int,user:int,role):
        """

        :param project:
        :param role_assigner:
        :param user:
        :param role:
        :return:
        """
        try:
            if not UserRoleValidator.is_operation_permitted(project,role_assigner,user,role):
                return False
            role = self.get(project_id=project,user_id=user)
            if role is None:
                return self.create(project_id=project,user_id=user,role=role)
            role.update(role=role)
        except ValueError:
            return False
        except django.db.DatabaseError as e:
            return False
class UserProjectRole(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    role = models.CharField(default='Developer')
    objects = UserRoleManager()
    class Meta:
        db_table = 'project_roles'
        unique_together = [['user', 'project']]

class ProjectTaskParticipation(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    task = models.ForeignKey(ProjectTask,on_delete=models.CASCADE,null=True,blank=True)
    class Meta:
        db_table = 'project_task_participations'

