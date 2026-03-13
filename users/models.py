from decouple import config
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from datetime import datetime

from django.db.models import Q
from multipledispatch import dispatch
class CustomUserManager(BaseUserManager):
    def create_user(self,username,email,password=None,**extra_fields):
        if not  username:
            raise ValueError('Trebuie username!')
        if not email:
            raise ValueError('Trebuie email')
        email = self.normalize_email(email)
        user = self.model(username=username,email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        UserProfileSection.objects.create_default_user_sections(user)
        UserTechnicalSkill.objects.create_default_user_techstack(user)
        return self.count(username=username) == 1;
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)
    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD:username})

class User(AbstractBaseUser,PermissionsMixin):
    username = models.CharField(max_length=100, blank=False, unique=True)
    login_date = models.DateTimeField(default=datetime.now)
    email = models.CharField(max_length=100, blank=False, unique=True)
    birthday = models.DateField(null=True,blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = CustomUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','password']
    class Meta:
        db_table = 'users'
        #managed = False

class UserProfileData(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to='users/profiles/%Y/%m/%d/',
        blank=True,
        null=True,
        default='users/profile_pictures/sbcf-default-avatar.png'
    )
    background_picture = models.ImageField(
        upload_to='users/background_pictures/%Y/%m/%d/',
        blank=True,
        null=True,
        default='users/background_pictures/sbcf-default-backgrounds.png'
    )
    biography = models.CharField(max_length=200,blank=False,default="Welcome to my profile!")
    class Meta:
        db_table = 'profile_datas'


class CustomUserProfileSectionManager(BaseUserManager):
    @dispatch(User,str,str,bool)
    def create_user_profile_section(self,user:User,name:str,content:str,hidden:bool):
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
        self.filter(Q(id=section_id)|Q(user_id=user.id)).delete()
        return self.filter(id=section_id).count() == 0
    @dispatch(User)
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
        return self.filter(Q(hidden=includehidden)|Q(user_id=user.id))
    def create_default_user_sections(self, user):
        """
        Creates the default user sections after the account gets created
        :param user:
        :return:None
        """
        from django.conf import settings
        sections_data = [
            UserProfileSection(user=user, name=key, content=value, hidden=False)
            for key, value in settings.DEFAULT_SECTIONS.items()
        ]
        UserProfileSection.objects.bulk_create(sections_data)

class UserProfileSection(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100,blank=False)
    content = models.CharField(max_length=500,blank=False)
    objects = CustomUserProfileSectionManager()
    hidden = models.BooleanField(default=False)
    class Meta:
        db_table = 'profile_sections'

class UserTechnicalSkillsManager(BaseUserManager):
    def add_user_skill(self,user):
        pass
    def remove_user_skill(self,user):
        pass

    def get_skills_from_section(self, section_id):
        """

        :param section_id:
        :return:
        """
        return self.filter(section_id=section_id)

class UserTechnicalSkill(models.Model):
    name = models.CharField(max_length=100,blank=False)
    section = models.ForeignKey(UserProfileSection,on_delete=models.CASCADE)
    objects = UserTechnicalSkillsManager()
    class Meta:
        db_table = 'technical_skills'

class UserTechnicalSkillSectionManager(BaseUserManager):
    def create_user_default_techstack(self,user):
        """
        Creates the default tech stack categories for any user profile after creating account
        :param user:
        :return:
        """
        default_sections = [
                UserTechnicalSkillSection(name=name,user_id=user.id)
                for name in config('DEFAULT_TECHSTACK_CATEGORIES')
        ]
        print(default_sections)
        self.bulk_create(default_sections)

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

class UserExperienceSubsection(models.Model):
    name = models.CharField(max_length=100,blank=False)
    description = models.CharField(max_length=500)
    user_section = models.ForeignKey(UserProfileSection,on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

