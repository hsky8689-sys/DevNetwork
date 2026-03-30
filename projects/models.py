from collections import defaultdict

import django.db
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
        UserProjectRole.objects.give_role(proj.owner,proj,default_roles[0][0].id)

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
        managed = False

class ProjectDomainManager(models.Manager):
    def add_domain_to_project(self,project,domain_name):
        item = self.model(domain=domain_name,project_id=project.id)
        item.save()
    def get_project_domains(self,project):
        return self.filter(project_id=project.id).values('domain')


class ProjectDomain(models.Model):
    project=models.ForeignKey(Project,on_delete=models.CASCADE)
    domain=models.CharField(max_length=100,blank=False,null=False,default='new domain')
    objects = ProjectDomainManager()

    class Meta:
        db_table = 'project_domains'

class ProjectTaskManager(models.Manager):
    def add_task_to_project(self):
        pass
    def remove_task_from_project(self):
        pass


class ProjectTask(models.Model):
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    name = models.CharField(max_length=100,default='New task',blank=True)
    description = models.CharField(max_length=300,default='Describe the task..',blank=True)
    start_date = models.DateField(default='1000-10-10')
    end_date = models.DateField(default='3000-10-10')
    finished = models.BooleanField(default=False)
    objects = ProjectTaskManager()
    class Meta:
        db_table = 'projects_tasks'
        managed = False
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
                role = ProjectRole.objects.get_or_create(
                    name=role_name,
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

class UserProjectRoleManager(models.Manager):
    def make_new_owner(self,project):
        """

        :param project:
        :return:
        """
    def give_role(self,user,project,role):
        role = self.model(user_id=user.id,project_id=project.id,role_id=role)
        role.save()
    def get_user_role_in_project(self, project, user):
        """
        Gets an user's role in a project if it exists,else labels them as visitors
        :param project:
        :param user:
        :return:
        """
        try:
            role_obj = self.get_queryset().filter(
                project=project,
                user=user
            ).select_related('role').first()
            return role_obj.role.name if role_obj else 'visitor'
        except UserProjectRole.DoesNotExist:
            return 'visitor'
    def get_role_permissions(self,role_name,project):
        try:
            user_project_role = self.get_queryset().select_related('role').filter(
                role__name=role_name,
                project=project
            ).first()

            if not user_project_role:
                return {
                    'can_accept_invites': False,
                    'can_invite_others': False,
                    'can_kick_others': False,
                    'can_change_roles': False,
                    'can_start_calls': False,
                    'can_add_tasks': False,
                    'can_delete_tasks': False,
                    'can_modify_tasks': False,
                    'can_change_project_settings': False,
                }
            role = user_project_role.role
            return {
                'can_accept_invites': role.can_accept_invites,
                'can_invite_others': role.can_invite_others,
                'can_kick_others': role.can_kick_others,
                'can_change_roles': role.can_change_roles,
                'can_start_calls': role.can_start_calls,
                'can_add_tasks': role.can_add_tasks,
                'can_delete_tasks': role.can_delete_tasks,
                'can_modify_tasks': role.can_modify_tasks,
                'can_change_project_settings': role.can_change_project_settings,
            }
        except Exception as e:
            print(str(e))
            return {k: False for k in [
                'can_accept_invites', 'can_invite_others', 'can_kick_others',
                'can_change_roles', 'can_start_calls', 'can_add_tasks',
                'can_delete_tasks', 'can_modify_tasks', 'can_change_project_settings'
            ]}
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
    def get_all_users_in_project(self, project):
        """
        Returns the whole users that ever participated/are participating now in a project
        :param project:
        :return: A dictionary with the participants grouped by the roles in the given project
        """
        users_by_role = defaultdict(list)
        roles = self.get_queryset().filter(project=project).select_related('user', 'role')
        for role_obj in roles:
            users_by_role[role_obj.role.name].append(role_obj.user)
        return dict(users_by_role)

class UserProjectRole(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,default=-1)
    project = models.ForeignKey(Project,on_delete=models.CASCADE,default=-1)
    role = models.ForeignKey(ProjectRole,on_delete=models.CASCADE,default=-1)
    objects = UserProjectRoleManager()
    class Meta:
        db_table = 'user_project_roles'

class ProjectTaskParticipation(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    task = models.ForeignKey(ProjectTask,on_delete=models.CASCADE,null=True,blank=True)
    class Meta:
        db_table = 'project_task_participations'
        managed = False