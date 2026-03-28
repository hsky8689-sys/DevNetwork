from collections import defaultdict

import django.db
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.decorators import login_required
from django.db import models

from users.models import User

class ProjectManager(models.Manager):
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
        default_roles = ProjectRole.objects.create_default_project_roles(proj)
        owner_role = default_roles[0]
        UserProjectRole.objects.give_role(proj.owner,proj,owner_role)

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

class Project(models.Model):
    owner=models.ForeignKey(User,on_delete=models.CASCADE)
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
        #is_assigner = UserRoleManager.is_user_in_project(_project,_role_assigner)
        #is_user = UserRoleManager.is_user_in_project(_project, _user)
        #if not is_assigner:
        #    raise ValueError("Assigner not found")
        #if not is_user:
        #    raise ValueError("User not found")
        #permission checking TODO
        return True

class ProjectRoleManager(models.Manager):
    def create_default_project_roles(self,project):
        try:
            from devnetwork.settings import DEFAULT_PROJECT_ROLES
            created_roles = []
            for role_name,role_permissions in DEFAULT_PROJECT_ROLES.items():
                role,created = self.get_or_create(
                    project_id=project.id,
                    role=role_name,
                    defaults=role_permissions
                )
                created_roles.append(role)
            return created_roles
        except django.db.Error as e:
            print(str(e))
    def modify_project_role(self,project,form):
        try:
            print('todo')
        except django.db.Error as e:
            print(str(e))
        except Exception as ex:
            print(str(ex))

class ProjectRole(models.Model):
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    name = models.CharField(max_length=50,default='new role',null=False,blank=True)
    can_accept_invites = models.BooleanField(default=False)
    can_invite_others = models.BooleanField(default=False)
    can_kick_others = models.BooleanField(default=False)
    can_change_roles = models.BooleanField(default=False)
    can_start_calls = models.BooleanField(default=False)
    can_add_tasks = models.BooleanField(default=False)
    can_delete_tasks = models.BooleanField(default=False)
    can_modify_tasks = models.BooleanField(default=False)
    can_change_project_settings = models.BooleanField(default=False)
    objects = ProjectRoleManager()
    class Meta:
        db_table = 'project_roles'
        managed = False

class UserProjectRoleManager(models.Manager):
    def make_new_owner(self,project):
        """

        :param project:
        :return:
        """
    def give_role(self,user,project,role):
        role = self.model(user_id=user,project_id=project,role_id=role)
        role.save()
    def get_user_role_in_project(self, project, user):
        """
        Checks if an user is already in a project
        :param project:
        :param user:
        :return:
        """
        try:
            role_set = self.filter(project_id=project.id,
                                   user_id=user.id).values('role').first()
            return role_set['role'] if role_set else 'visitor'
        except ValueError as v:
            print(str(v))
        except django.db.DatabaseError as e:
            print(str(e))
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
    @login_required
    def get_all_users_in_project(self, project):
        """
        Returns the whole users that ever participated/are participating now in a project
        :param project:
        :return: A dictionary with the participants grouped by the roles in the given project
        """
        try:
            roles = self.filter(project=project).select_related('user')
            users_by_role = defaultdict(list)
            for role_obj in roles:
                users_by_role[role_obj.role].append(role_obj.user)
            return dict(users_by_role)
        except Exception as e:
            print(str(e))
            return defaultdict(list)
class UserProjectRole(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    role = models.ForeignKey(ProjectRole,on_delete=models.CASCADE)
    objects = UserProjectRoleManager()
    class Meta:
        db_table = 'user_project_roles'
        managed = False

class ProjectTaskParticipation(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    task = models.ForeignKey(ProjectTask,on_delete=models.CASCADE,null=True,blank=True)
    class Meta:
        db_table = 'project_task_participations'