from django.contrib import admin

from .models import Client, Invoice, InvoiceLine, Payment, Project, TimeEntry, TimeEntryEvent, User

admin.site.site_header = 'Copetrolite — Administration'
admin.site.site_title = 'Copetrolite'
admin.site.index_title = 'Consultation des données'


class ReadOnlyAdmin(admin.ModelAdmin):
    """All writes use the API so admin cannot bypass workflow or audit checks."""
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(ReadOnlyAdmin):
    exclude = ['password', 'user_permissions', 'groups']
    list_display = ['username', 'first_name', 'last_name', 'role', 'client', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'first_name', 'last_name']


@admin.register(TimeEntry)
class TimeEntryAdmin(ReadOnlyAdmin):
    list_display = ['technician', 'project', 'start', 'end', 'hours', 'status', 'reviewed_by']
    list_filter = ['status', 'project']


@admin.register(Project)
class ProjectAdmin(ReadOnlyAdmin):
    list_display = ['name', 'client', 'site', 'manager_name', 'status']
    list_filter = ['status', 'client']


for model in [Client, Invoice, InvoiceLine, Payment, TimeEntryEvent]:
    admin.site.register(model, ReadOnlyAdmin)
