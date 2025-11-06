from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.db import models



class UserManager(BaseUserManager):
    def active_users(self):
        return self.filter(is_active=True)

    def inactive_users(self):
        return self.filter(is_active=False)

    def verified_users(self):
        return self.filter(is_verified=True)

    def unverified_users(self):
        return self.filter(is_verified=False)

    # Role-based filters
    def admins(self):
        return self.filter(role='admin')

    def authors(self):
        return self.filter(role='author')

    def moderators(self):
        return self.filter(role='moderator')

    def editors(self):
        return self.filter(role='editor')

    def customers(self):
        return self.filter(role='customer')
    


class User(AbstractUser):
    ROLE_ADMIN = "admin"
    ROLE_AUTHOR = "author"
    ROLE_MODERATOR = "moderator"
    ROLE_CUSTOMER = "customer"
    ROLE_EDITOR = "editor"

    ROLE_CHOICES = (
        (ROLE_ADMIN, "Admin"),
        (ROLE_AUTHOR, "Author"),
        (ROLE_MODERATOR, "Moderator"),
        (ROLE_CUSTOMER, "Customer"),
        (ROLE_EDITOR, "Editor"),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True, default="profiles/default.png")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[("male","Male"),("female","Female")], blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    def __str__(self):
        return self.username
    
    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def is_author(self):
        return self.role == self.ROLE_AUTHOR

    @property
    def is_moderator(self):
        return self.role == self.ROLE_MODERATOR

    @property
    def is_editor(self):
        return self.role == self.ROLE_EDITOR

    @property
    def is_customer(self):
        return self.role == self.ROLE_CUSTOMER