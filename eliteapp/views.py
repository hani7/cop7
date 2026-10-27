from decimal import Decimal
import base64

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.db.models import Prefetch, Q
from django.db.models.deletion import ProtectedError
from django.http import FileResponse, Http404
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from .access import entries_for, projects_for, require_role
from .models import Client, Invoice, Payment, Project, PublicHoliday, TechnicianCertificate, TimeEntry, User
from .serializers import (ClientSerializer, InvoiceCreateSerializer, InvoiceSerializer,
                          PaymentSerializer, ProjectSerializer, PublicHolidaySerializer,
                          TimeEntrySerializer, UserSerializer)
from .services import create_invoice, record_payment, transition_entry
from .cv import extract_cv, extract_cv_photo


def session_data(user):
    project = Project.objects.filter(access_user=user).values('id', 'name').first()
    return {'id': user.pk, 'username': user.username, 'full_name': user.get_full_name() or user.username,
            'role': user.effective_role, 'client': user.client_id, 'currency': settings.APP_CURRENCY,
            'project_access': project}


class LoginThrottle(AnonRateThrottle):
    scope = 'login'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class SessionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'user': session_data(request.user) if request.user.is_authenticated else None,
                         'csrfToken': get_token(request)})


@method_decorator(csrf_protect, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]
    project_only = False

    def post(self, request):
        username, password = request.data.get('username'), request.data.get('password')
        if not isinstance(username, str) or not isinstance(password, str):
            raise ValidationError('Identifiant et mot de passe requis.')
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({'detail': 'Identifiant ou mot de passe incorrect.'}, status=400)
        if self.project_only and (
            user.effective_role != User.Role.PROJECT_MANAGER
            or not Project.objects.filter(access_user=user, client_id=user.client_id, client__is_active=True).exists()
        ):
            return Response({'detail': 'Cet accès est réservé aux comptes clients des projets.'}, status=403)
        login(request, user)
        return Response({'user': session_data(user), 'csrfToken': get_token(request)})


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'detail': 'Déconnexion effectuée.'})


class EditableViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """Archive records instead of deleting business history."""
    http_method_names = ['get', 'post', 'patch', 'head', 'options']


class ClientViewSet(EditableViewSet):
    serializer_class = ClientSerializer
    http_method_names = [*EditableViewSet.http_method_names, 'delete']

    def get_queryset(self):
        user = self.request.user
        if user.effective_role in [User.Role.ADMIN, User.Role.SUPERVISOR]:
            return Client.objects.all()
        return Client.objects.filter(pk__in=projects_for(user).values('client_id'))

    def perform_create(self, serializer):
        require_role(self.request.user, User.Role.ADMIN, User.Role.SUPERVISOR)
        serializer.save()

    def perform_update(self, serializer):
        self.perform_create(serializer)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        require_role(request.user, User.Role.ADMIN)
        client = self.get_object()
        if client.projects.exists() or User.objects.filter(client=client).exists():
            raise ValidationError('Ce client est lié à des projets ou à des comptes chef de projet. Désactivez-le pour conserver l’historique.')
        logo = client.logo
        client.delete()
        if logo:
            transaction.on_commit(
                lambda storage=logo.storage, name=logo.name: storage.delete(name),
                robust=True,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='logo')
    def download_logo(self, request, pk=None):
        client = self.get_object()
        if not client.logo:
            raise Http404
        extension = client.logo.name.rsplit('.', 1)[-1].lower()
        content_type = {
            'png': 'image/png',
            'webp': 'image/webp',
            'avif': 'image/avif',
        }.get(extension, 'image/jpeg')
        try:
            response = FileResponse(client.logo.open('rb'), content_type=content_type)
        except FileNotFoundError as exc:
            raise Http404 from exc
        response['Cache-Control'] = 'private, no-store'
        response['X-Content-Type-Options'] = 'nosniff'
        return response


class UserViewSet(EditableViewSet):
    serializer_class = UserSerializer
    http_method_names = [*EditableViewSet.http_method_names, 'delete']

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        require_role(request.user, User.Role.ADMIN)
        technician = self.get_object()
        technician = User.objects.select_for_update().get(pk=technician.pk)
        if (technician.pk == request.user.pk or technician.role != User.Role.TECHNICIAN
                or technician.is_superuser or technician.is_staff):
            raise ValidationError('Seuls les comptes techniciens sans accès administrateur peuvent être supprimés.')
        if technician.assigned_projects.exists() or technician.time_entries.exists():
            raise ValidationError('Ce technicien est lié à des projets ou pointages. Désactivez son compte depuis Modifier pour conserver l’historique.')
        files = [document.file for document in technician.certificate_documents.all()]
        for field in [technician.cv, technician.photo]:
            if field:
                files.append(field)
        try:
            technician.delete()
        except ProtectedError as exc:
            raise ValidationError('Ce compte est lié à un historique. Désactivez-le depuis Modifier plutôt que de le supprimer.') from exc
        for file in files:
            transaction.on_commit(lambda storage=file.storage, name=file.name: storage.delete(name), robust=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path=r'certificates/(?P<certificate_id>\d+)')
    def download_certificate(self, request, pk=None, certificate_id=None):
        require_role(request.user, User.Role.ADMIN, User.Role.SUPERVISOR)
        user = self.get_object()
        try:
            document = user.certificate_documents.get(pk=certificate_id)
            response = FileResponse(document.file.open('rb'), as_attachment=request.query_params.get('preview') != '1',
                                    filename=document.name)
        except (TechnicianCertificate.DoesNotExist, FileNotFoundError) as exc:
            raise Http404 from exc
        response['Cache-Control'] = 'private, no-store'
        response['X-Content-Type-Options'] = 'nosniff'
        return response

    @action(detail=False, methods=['post'], url_path='extract-cv')
    def extract_resume(self, request):
        require_role(request.user, User.Role.ADMIN)
        upload = request.FILES.get('cv')
        if not upload:
            raise ValidationError({'cv': 'Sélectionnez un CV à lire.'})
        return Response(extract_cv(upload))

    @action(detail=False, methods=['post'], url_path='extract-cv-photo')
    def extract_resume_photo(self, request):
        require_role(request.user, User.Role.ADMIN)
        upload = request.FILES.get('cv')
        if not upload:
            raise ValidationError({'cv': 'Sélectionnez un CV pour en extraire la photo.'})
        photo = extract_cv_photo(upload)
        if not photo:
            raise ValidationError({'cv': 'Aucune photo exploitable n’a été trouvée dans ce CV. Ajoutez une photo manuellement.'})
        return Response({'photo': base64.b64encode(photo).decode('ascii')})

    @action(detail=True, methods=['post'], url_path='extract-cv-photo')
    def extract_saved_resume_photo(self, request, pk=None):
        require_role(request.user, User.Role.ADMIN)
        user = self.get_object()
        if not user.cv:
            raise ValidationError({'cv': 'Aucun CV enregistré sur cette fiche.'})
        try:
            with user.cv.open('rb') as upload:
                photo = extract_cv_photo(upload)
        except FileNotFoundError as exc:
            raise Http404 from exc
        if not photo:
            raise ValidationError({'cv': 'Aucune photo exploitable n’a été trouvée dans ce CV. Ajoutez une photo manuellement.'})
        return Response({'photo': base64.b64encode(photo).decode('ascii')})

    @action(detail=True, methods=['post'], url_path='extract-cv')
    def extract_saved_resume(self, request, pk=None):
        require_role(request.user, User.Role.ADMIN)
        user = self.get_object()
        if not user.cv:
            raise ValidationError({'cv': 'Aucun CV enregistré sur cette fiche.'})
        try:
            with user.cv.open('rb') as upload:
                result = extract_cv(upload)
        except FileNotFoundError as exc:
            raise Http404 from exc
        return Response(result)

    @action(detail=True, methods=['get'], url_path='photo')
    def download_photo(self, request, pk=None):
        require_role(request.user, User.Role.ADMIN, User.Role.SUPERVISOR)
        user = self.get_object()
        if not user.photo:
            raise Http404
        extension = user.photo.name.rsplit('.', 1)[-1].lower()
        content_type = {
            'png': 'image/png',
            'webp': 'image/webp',
            'avif': 'image/avif',
        }.get(extension, 'image/jpeg')
        try:
            response = FileResponse(user.photo.open('rb'), content_type=content_type)
        except FileNotFoundError as exc:
            raise Http404 from exc
        response['Cache-Control'] = 'private, no-store'
        response['X-Content-Type-Options'] = 'nosniff'
        return response

    @action(detail=True, methods=['get'], url_path='cv')
    def download_cv(self, request, pk=None):
        require_role(request.user, User.Role.ADMIN, User.Role.SUPERVISOR)
        user = self.get_object()
        if not user.cv:
            raise Http404
        try:
            response = FileResponse(user.cv.open('rb'), as_attachment=request.query_params.get('preview') != '1',
                                    filename=user.cv.name.rsplit('/', 1)[-1])
        except FileNotFoundError as exc:
            raise Http404 from exc
        response['Cache-Control'] = 'private, no-store'
        response['X-Content-Type-Options'] = 'nosniff'
        return response

    def get_queryset(self):
        user = self.request.user
        if user.effective_role in [User.Role.ADMIN, User.Role.SUPERVISOR]:
            return User.objects.select_related('client').prefetch_related('certificate_documents').all()
        if user.effective_role == User.Role.PROJECT_MANAGER:
            projects = projects_for(user)
            return User.objects.filter(role=User.Role.TECHNICIAN,
                                       assigned_projects__in=projects).distinct()
        return User.objects.filter(pk=user.pk)

    def create(self, request, *args, **kwargs):
        require_role(request.user, User.Role.ADMIN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        require_role(request.user, User.Role.ADMIN)
        return super().update(request, *args, **kwargs)


class ProjectViewSet(EditableViewSet):
    serializer_class = ProjectSerializer

    @action(detail=True, methods=['get', 'post'], url_path='access')
    @transaction.atomic
    def client_access(self, request, pk=None):
        require_role(request.user, User.Role.ADMIN)
        project = Project.objects.select_for_update().get(pk=self.get_object().pk)
        account = project.access_user
        created = account is None
        if request.method == 'POST':
            if not project.client.is_active:
                raise ValidationError('Ce client est désactivé.')
            # Only credentials and activation can be set through this endpoint.
            payload = {key: request.data[key] for key in ['username', 'password', 'is_active'] if key in request.data}
            if created:
                payload.update(role=User.Role.PROJECT_MANAGER, client=project.client_id,
                               first_name=project.manager_name[:150])
            serializer = UserSerializer(account, data=payload, partial=not created, context={'request': request})
            serializer.is_valid(raise_exception=True)
            account = serializer.save()
            if created:
                project.access_user = account
                project.save(update_fields=['access_user'])
        return Response({
            'project': project.pk,
            'username': account.username if account else '',
            'is_active': account.is_active if account else False,
            'configured': account is not None,
            'login_path': '/project/login',
        }, status=status.HTTP_201_CREATED if request.method == 'POST' and created else status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def earnings(self, request):
        require_role(request.user, User.Role.TECHNICIAN)
        entries = entries_for(request.user).filter(status__in=['APPROVED', 'INVOICED'])
        projects = projects_for(request.user).select_related('client').prefetch_related(
            Prefetch('time_entries', queryset=entries, to_attr='cost_entries'),
        )
        page = self.paginate_queryset(projects)
        cost_serializer = ProjectSerializer()
        rows = [{
            'id': project.pk,
            'name': project.name,
            'client_name': project.client.name,
            'site': project.site,
            'status': project.status,
            'hours': str(sum((entry.hours for entry in project.cost_entries), Decimal('0.00'))),
            'hourly_rate': str(project.technician_hourly_rate),
            'holiday_day_rate': str(project.holiday_day_rate),
            'amount': str(cost_serializer.get_technician_labor_cost(project)),
            'currency': settings.APP_CURRENCY,
        } for project in (page if page is not None else projects)]
        return self.get_paginated_response(rows) if page is not None else Response(rows)

    def get_queryset(self):
        cost_entries = TimeEntry.objects.filter(status__in=['APPROVED', 'INVOICED']).select_related('technician')
        return projects_for(self.request.user).select_related('client', 'project_manager').prefetch_related(
            'technicians', Prefetch('time_entries', queryset=cost_entries, to_attr='cost_entries'),
        )

    def create(self, request, *args, **kwargs):
        require_role(request.user, User.Role.ADMIN, User.Role.SUPERVISOR)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        require_role(request.user, User.Role.ADMIN, User.Role.SUPERVISOR)
        Project.objects.select_for_update().get(pk=self.get_object().pk)
        return super().update(request, *args, **kwargs)


class PublicHolidayViewSet(mixins.DestroyModelMixin, EditableViewSet):
    serializer_class = PublicHolidaySerializer
    http_method_names = [*EditableViewSet.http_method_names, 'delete']

    def get_queryset(self):
        require_role(self.request.user, User.Role.ADMIN)
        return PublicHoliday.objects.all()

    def perform_create(self, serializer):
        require_role(self.request.user, User.Role.ADMIN)
        serializer.save()

    def perform_update(self, serializer):
        require_role(self.request.user, User.Role.ADMIN)
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        require_role(request.user, User.Role.ADMIN)
        return super().destroy(request, *args, **kwargs)


class TimeEntryViewSet(EditableViewSet):
    serializer_class = TimeEntrySerializer

    def get_queryset(self):
        qs = entries_for(self.request.user).select_related('technician', 'project__client').prefetch_related('events__actor')
        if self.request.query_params.get('status'):
            qs = qs.filter(status=self.request.query_params['status'])
        return qs

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        require_role(request.user, User.Role.TECHNICIAN)
        User.objects.select_for_update().get(pk=request.user.pk)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        require_role(request.user, User.Role.TECHNICIAN)
        User.objects.select_for_update().get(pk=request.user.pk)
        TimeEntry.objects.select_for_update().get(pk=self.get_object().pk)
        return super().update(request, *args, **kwargs)

    def transition(self, request, action_name):
        reason = request.data.get('reason', '')
        if not isinstance(reason, str) or len(reason) > 2000:
            raise ValidationError({'reason': 'Le motif doit être un texte de 2 000 caractères maximum.'})
        entry = transition_entry(self.get_object().pk, request.user, action_name, reason)
        return Response(self.get_serializer(entry).data)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        return self.transition(request, 'submit')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        return self.transition(request, 'approve')

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        return self.transition(request, 'reject')


class InvoiceViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        require_role(self.request.user, User.Role.ADMIN)
        return Invoice.objects.prefetch_related('lines', 'payments')

    def create(self, request, *args, **kwargs):
        require_role(request.user, User.Role.ADMIN)
        serializer = InvoiceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice = create_invoice(request.user, **serializer.validated_data)
        return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)


class PaymentViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        require_role(self.request.user, User.Role.ADMIN)
        return Payment.objects.all()

    def create(self, request, *args, **kwargs):
        require_role(request.user, User.Role.ADMIN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = record_payment(request.user, **serializer.validated_data)
        return Response(self.get_serializer(payment).data, status=status.HTTP_201_CREATED)


class DashboardView(APIView):
    def get(self, request):
        entries = entries_for(request.user)
        total_hours = sum((entry.hours for entry in entries), Decimal('0.00'))
        result = {
            'active_projects': projects_for(request.user).filter(status='ACTIVE').count(),
            'total_hours': str(total_hours),
            'pending_entries': entries.filter(status='SUBMITTED').count(),
            'approved_hours': str(sum((e.hours for e in entries.filter(status='APPROVED')), Decimal('0.00'))),
        }
        if request.user.effective_role == User.Role.ADMIN:
            invoices = list(Invoice.objects.prefetch_related('payments'))
            result['outstanding'] = str(sum((invoice.balance for invoice in invoices), Decimal('0.00')))
            result['received'] = str(sum((invoice.paid for invoice in invoices), Decimal('0.00')))
        return Response(result)
