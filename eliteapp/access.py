from django.db.models import Q
from rest_framework.exceptions import PermissionDenied

from .models import Project, TimeEntry, User


def require_role(user, *roles):
    if user.effective_role not in roles:
        raise PermissionDenied('Vous ne disposez pas des droits nécessaires.')


def projects_for(user):
    queryset = Project.objects.filter(deleted_at__isnull=True, client__deleted_at__isnull=True)
    if user.effective_role in [User.Role.ADMIN, User.Role.SUPERVISOR]:
        return queryset
    if user.effective_role == User.Role.PROJECT_MANAGER:
        dedicated = queryset.filter(access_user=user)
        if dedicated.exists():
            return dedicated.filter(client_id=user.client_id, client__is_active=True)
        return queryset.filter(project_manager=user, client_id=user.client_id, client__is_active=True)
    return queryset.filter(Q(technicians=user) | Q(time_entries__technician=user)).distinct()


def entries_for(user):
    queryset = TimeEntry.objects.all()
    if user.effective_role in [User.Role.ADMIN, User.Role.SUPERVISOR]:
        return queryset
    if user.effective_role == User.Role.PROJECT_MANAGER:
        return queryset.filter(project__in=projects_for(user)).exclude(status='DRAFT')
    return queryset.filter(technician=user)
