from django.contrib import admin
from .models import Organization, OrganizationUser, DataSource


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin_email', 'created_at')
    search_fields = ('name', 'admin_email')


@admin.register(OrganizationUser)
class OrganizationUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'created_at')
    list_filter = ('role', 'organization')
    search_fields = ('user__email', 'organization__name')


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'source_type', 'created_at')
    list_filter = ('source_type', 'organization')
    search_fields = ('name', 'organization__name')
