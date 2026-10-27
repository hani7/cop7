from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ClientViewSet, DashboardView, InvoiceViewSet, LoginView, LogoutView,
                    PaymentViewSet, ProjectViewSet, PublicHolidayViewSet, SessionView,
                    TechnicianPaymentViewSet,
                    TimeEntryViewSet, UserViewSet)

router = DefaultRouter()
router.register('clients', ClientViewSet, basename='client')
router.register('users', UserViewSet, basename='user')
router.register('projects', ProjectViewSet, basename='project')
router.register('holidays', PublicHolidayViewSet, basename='holiday')
router.register('time-entries', TimeEntryViewSet, basename='time-entry')
router.register('invoices', InvoiceViewSet, basename='invoice')
router.register('payments', PaymentViewSet, basename='payment')
router.register('technician-payments', TechnicianPaymentViewSet, basename='technician-payment')

urlpatterns = [
    path('auth/session/', SessionView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('auth/project-login/', LoginView.as_view(project_only=True)),
    path('auth/logout/', LogoutView.as_view()),
    path('dashboard/', DashboardView.as_view()),
    path('', include(router.urls)),
]
