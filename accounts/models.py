from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    """
    Custom User model to include user roles (applicant/employer).
    """
    USER_TYPE_CHOICES = (
        ('applicant', 'Applicant'),
        ('employer', 'Employer'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='applicant')

    # Add related_name to avoid clashes with default User model's groups and user_permissions
    # These are necessary when you extend AbstractUser directly.
    groups = models.ManyToManyField(
        Group,
        related_name='accounts_user_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='accounts_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def is_applicant(self):
        """
        Helper method to check if the user is an applicant.
        """
        return self.user_type == 'applicant'

    def is_employer(self):
        """
        Helper method to check if the user is an employer.
        """
        return self.user_type == 'employer'

    def __str__(self):
        return self.username