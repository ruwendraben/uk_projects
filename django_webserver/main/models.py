from django.db import models
from django.contrib.auth.models import User


class Organization(models.Model):
    """Represents an organization that can onboard to the system."""
    name = models.CharField(max_length=255, unique=True)
    admin_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class OrganizationUser(models.Model):
    """Links users to organizations with role-based access."""
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('viewer', 'Viewer'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'organization')

    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.role})"


class DataSource(models.Model):
    """Represents a data source connected to an organization."""
    SOURCE_TYPES = [
        ('postgresql', 'PostgreSQL'),
        ('mysql', 'MySQL'),
        ('csv', 'CSV File'),
    ]
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    connection_string = models.TextField()  # TODO: Encrypt using django-cryptography
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('organization', 'name')

    def __str__(self):
        return f"{self.organization.name} - {self.name}"
