from django.contrib.auth.base_user import BaseUserManager
from django.db import models
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

class Project(models.Model):
    owner=models.ForeignKey(User,on_delete=ProjectManager.makeNewOwner)
    class Meta:
        db_table = 'projects'

class ProjectTask(models.Model):
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    class Meta:
        db_table = 'projects_tasks'

class UserProjectRole(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    role = models.CharField(default='Developer')
    class Meta:
        db_table = 'project_roles'
class ProjectTaskParticipation(models.Model):
    class Meta:
        db_table = 'project_task_participations'
