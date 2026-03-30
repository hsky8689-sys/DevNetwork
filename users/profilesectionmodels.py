from django.contrib.auth.models import BaseUserManager
from django.db import models

from devnetwork import settings

User = settings.AUTH_USER_MODEL
class CustomUserProfileSectionManager(BaseUserManager):
    def create_user_profile_section(self,user:settings.AUTH_USER_MODEL,name:str,content:str,hidden:bool):
        """
        Creates a new profile section with no which will be added to an user's personal page
        :param user: The specified user
        :param name: The new section's name (Non-empty at least 100 characters)
        :param content: The new section's content (Non-empty at least 100 characters)
        :param hidden: States if the section will be or not hidden to foreign profile visitors
        :return: None
        """
        new_section = (self.create(user=user,
                               name=name,
                               content=content,
                               hidden=hidden
                               ))
        new_section.save()
    def delete_user_profile_section(self,user:User,section_id):
        """
        Deletes a former profile section from an user's personal page
        :param user:
        :return:true or false if the section was updated accordingly
        """
        self.filter(id=section_id,user_id=user.id).delete()
        return self.filter(id=section_id).count() == 0

    def update_user_profile_section(self,user,new_section)->bool:
        """
        Updates a user's profile section
        :param user:
        :return: true or false if the section was updated accordingly
        """
        former_section = UserProfileSection.objects.get(id=new_section.id)
        if former_section is None:
            return False
        former_section.name = new_section.name
        former_section.content = new_section.content
        former_section.hidden = new_section.hidden
        return True
    def get_user_profile_sections(self,user,includehidden=False):
        """
        :param user:
        :param includehidden:
        :return:
        """
        if user is None:
            return []
        return self.filter(user_id=user.id,hidden=includehidden)
    def create_default_user_sections(self, user_id):
        """
        Creates the default user sections after the account gets created
        :param user_id:
        :return:None
        """
        from django.conf import settings
        import django.db as db
        if User.objects.get(id=user_id) is None:
            raise ValueError('There is no user with the given id')

        print(User.objects.get(id=user_id))
        try:
            sections_data = [
                UserProfileSection(user_id=user_id, name=key, content=value, hidden=False)
                for key, value in settings.DEFAULT_SECTIONS.items()
            ]
            print(sections_data)
            UserProfileSection.objects.bulk_create(sections_data,ignore_conflicts=True)
        except db.OperationalError as e:
            print(str(e))
        except db.Error as e:
            print(str(e))
        except RuntimeError as e:
            print(f'Unknown error of type{type(e)} with content {str(e)}')
        except Exception as e:
            print(f'Unknown error of type{type(e)} with content {str(e)}')

class UserProfileSection(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100,blank=False)
    content = models.CharField(max_length=500,blank=False)
    objects = CustomUserProfileSectionManager()
    hidden = models.BooleanField(default=False)
    class Meta:
        db_table = 'profile_sections'

class UserTechnicalSkillsManager(BaseUserManager):
    def add_user_skill(self,name,section_id):
        """

        :param name:
        :param section_id:
        :return:
        """
        return self.create(name=name,section_id=section_id) is not None

    def remove_user_skill(self,skill):
        """

        :param skill:
        :return:
        """
        return self.get(id=skill.id).delete()
    def get_skills_from_section(self, section_id):
        """

        :param section_id:
        :return:
        """
        return self.filter(section_id=section_id)

class UserTechnicalSkillSectionManager(BaseUserManager):
    def create_user_default_techstack(self,user_id):
        """
        Creates the default tech stack categories for any user profile after creating account
        :param user_id:
        :return:
        """
        from django.conf import settings
        if User.objects.get(id=user_id) is None:
            raise ValueError('There is no user with the given id')
        default_techstack = [
            UserTechnicalSkillSection(user_id=user_id, name=value)
            for value in settings.DEFAULT_TECHSTACK_CATEGORIES
        ]
        print(default_techstack)
        self.bulk_create(default_techstack)

    def get_user_techstack(self,user):
        """
        Returns an user's whole techstack
        :param user:
        :return:A dictionary with elements of type "tech-stack category":"User skills from that one category"
        """
        sections = self.filter(user=user)
        tech_dict = {}
        for section in sections:
            tech_dict[section] = []
            for skill in UserTechnicalSkill.objects.get_skills_from_section(section.id):
                tech_dict[section].append(skill)
        return tech_dict

class UserTechnicalSkillSection(models.Model):
    name = models.CharField(max_length=100,blank=False)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    objects = UserTechnicalSkillSectionManager()
    class Meta:
        db_table = 'technical_skill_sections'

class UserTechnicalSkill(models.Model):
    name = models.CharField(max_length=100,blank=False)
    section = models.ForeignKey(UserTechnicalSkillSection,on_delete=models.CASCADE)

    objects = UserTechnicalSkillsManager()
    class Meta:
        db_table = 'technical_skills'

class UserExperienceSubsection(models.Model):
    name = models.CharField(max_length=100,default='Add your experience working on this project',blank=True)
    description = models.CharField(max_length=500)
    user_section = models.ForeignKey(UserProfileSection,on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()