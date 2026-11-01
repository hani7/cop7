from django.contrib import admin
from django.utils import timezone

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
        return True


class TrashAdmin(ReadOnlyAdmin):
    """Admin deletion archives records so they remain restorable."""
    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True)

    def has_delete_permission(self, request, obj=None):
        return True

    @admin.action(description='Déplacer les éléments sélectionnés vers la corbeille')
    def move_selected_to_trash(self, request, queryset):
        queryset.update(deleted_at=timezone.now())

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        actions['move_selected_to_trash'] = (self.move_selected_to_trash, 'move_selected_to_trash', self.move_selected_to_trash.short_description)
        return actions

    def delete_model(self, request, obj):
        obj.deleted_at = timezone.now()
        obj.save(update_fields=['deleted_at'])

    def delete_queryset(self, request, queryset):
        queryset.update(deleted_at=timezone.now())


@admin.register(User)
class UserAdmin(TrashAdmin):
    exclude = ['password', 'user_permissions', 'groups']
    list_display = ['username', 'first_name', 'last_name', 'role', 'client', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'first_name', 'last_name']

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(TimeEntry)
class TimeEntryAdmin(ReadOnlyAdmin):
    list_display = ['technician', 'project', 'start', 'end', 'hours', 'status', 'reviewed_by']
    list_filter = ['status', 'project']


@admin.register(Project)
class ProjectAdmin(TrashAdmin):
    list_display = ['name', 'client', 'site', 'manager_name', 'status']
    list_filter = ['status', 'client']


@admin.register(Client)
class ClientAdmin(TrashAdmin):
    list_display = ['name', 'contact_name', 'is_active']
    search_fields = ['name', 'contact_name']


for model in [Invoice, InvoiceLine, Payment, TimeEntryEvent]:
    admin.site.register(model, ReadOnlyAdmin)
