from datetime import timedelta
from copy import copy
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from uuid import uuid4

from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import (Client, Invoice, InvoiceLine, Payment, Project, PublicHoliday, TechnicianCertificate,
                     TechnicianSequence, TimeEntry, TimeEntryEvent, User)
from .cv import extract_cv_photo, validate_certificate, validate_cv, validate_profile_photo


class ClientSerializer(serializers.ModelSerializer):
    logo = serializers.FileField(write_only=True, required=False, validators=[validate_profile_photo])
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ['id', 'name', 'contact_name', 'email', 'phone', 'rc', 'nif',
                  'article_number', 'nis', 'billing_address', 'start_work_date',
                  'logo', 'logo_url', 'is_active']

    def to_internal_value(self, data):
        if getattr(data.get('logo'), 'size', None) == 0:
            data = copy(data)
            data.pop('logo')
        return super().to_internal_value(data)

    def get_logo_url(self, obj):
        return f'/api/clients/{obj.pk}/logo/' if obj.logo else ''

    def update(self, instance, validated_data):
        previous_logo = instance.logo
        instance = super().update(instance, validated_data)
        if previous_logo and previous_logo.name != instance.logo.name:
            transaction.on_commit(
                lambda storage=previous_logo.storage, name=previous_logo.name: storage.delete(name),
                robust=True,
            )
        return instance


class TechnicianCertificateSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = TechnicianCertificate
        fields = ['id', 'name', 'url']

    def get_url(self, obj):
        return f'/api/users/{obj.user_id}/certificates/{obj.pk}/'


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, trim_whitespace=False)
    full_name = serializers.SerializerMethodField()
    client_name = serializers.CharField(source='client.name', read_only=True, default='')
    cv = serializers.FileField(write_only=True, required=False, validators=[validate_cv])
    cv_name = serializers.SerializerMethodField()
    cv_url = serializers.SerializerMethodField()
    photo = serializers.FileField(write_only=True, required=False, validators=[validate_profile_photo])
    photo_url = serializers.SerializerMethodField()
    certificate_documents = TechnicianCertificateSerializer(many=True, read_only=True)
    certificate_files = serializers.ListField(
        child=serializers.FileField(validators=[validate_certificate]), max_length=20,
        write_only=True, required=False,
    )
    remove_certificate_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), write_only=True, required=False,
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'full_name', 'email',
                  'role', 'client', 'client_name', 'phone', 'specialty', 'employee_number',
                  'hourly_cost', 'is_active', 'birth_date', 'assignment_date', 'address', 'experience', 'certificates',
                  'cv', 'cv_name', 'cv_url', 'photo', 'photo_url', 'certificate_documents',
                  'certificate_files', 'remove_certificate_ids']
        read_only_fields = ['employee_number']

    def validate_remove_certificate_ids(self, values):
        owned = set(self.instance.certificate_documents.values_list('id', flat=True)) if self.instance else set()
        if not set(values).issubset(owned):
            raise serializers.ValidationError('Un certificat sélectionné ne fait pas partie de cette fiche.')
        return list(set(values))

    def to_internal_value(self, data):
        # Empty optional files are omitted, preserving previously saved documents.
        if any(getattr(data.get(field), 'size', None) == 0 for field in ['cv', 'photo']):
            data = copy(data)
            for field in ['cv', 'photo']:
                if getattr(data.get(field), 'size', None) == 0:
                    data.pop(field)
        return super().to_internal_value(data)

    def get_cv_name(self, obj):
        return obj.cv.name.rsplit('/', 1)[-1] if obj.cv else ''

    def get_cv_url(self, obj):
        return f'/api/users/{obj.pk}/cv/' if obj.cv else ''

    def get_photo_url(self, obj):
        return f'/api/users/{obj.pk}/photo/' if obj.photo else ''

    def validate_birth_date(self, value):
        if value:
            today = timezone.localdate()
            if value > today:
                raise serializers.ValidationError('La date de naissance ne peut pas être future.')
            if (value.year, value.month, value.day) > (today.year - 18, today.month, today.day):
                raise serializers.ValidationError('Le technicien doit avoir au moins 18 ans.')
        return value

    def validate_phone(self, value):
        if value and (len(value) != 10 or not value.isascii() or not value.isdigit()):
            raise serializers.ValidationError('Le numéro de téléphone doit contenir exactement 10 chiffres.')
        return value

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request and request.user.effective_role not in [User.Role.ADMIN, User.Role.SUPERVISOR]:
            allowed = ['id', 'first_name', 'last_name', 'full_name', 'role', 'specialty', 'is_active']
            fields = {key: value for key, value in fields.items() if key in allowed}
        return fields

    def validate(self, attrs):
        role = attrs.get('role', getattr(self.instance, 'role', User.Role.TECHNICIAN))
        client = attrs.get('client', getattr(self.instance, 'client', None))
        if role == User.Role.TECHNICIAN:
            for field in ['last_name', 'first_name', 'specialty', 'address']:
                value = attrs.get(field, getattr(self.instance, field, ''))
                if isinstance(value, str):
                    attrs[field] = value.upper()
        if (role == User.Role.PROJECT_MANAGER) != bool(client):
            raise serializers.ValidationError({'client': 'Le chef de projet doit être rattaché à un client ; les autres rôles sont internes.'})
        if client and not client.is_active:
            raise serializers.ValidationError({'client': 'Ce client est désactivé.'})
        if attrs.get('hourly_cost', 0) < 0:
            raise serializers.ValidationError({'hourly_cost': 'Le coût doit être positif ou nul.'})
        if self.instance:
            changed = role != self.instance.role or client != self.instance.client
            if changed and (hasattr(self.instance, 'access_project') or self.instance.managed_projects.exists() or self.instance.assigned_projects.exists()
                            or self.instance.time_entries.exists()):
                raise serializers.ValidationError('Impossible de changer le rôle ou le client d’un utilisateur lié à des projets ou pointages.')
            if self.instance.pk == self.context['request'].user.pk and (
                role != self.instance.role or attrs.get('is_active') is False
            ):
                raise serializers.ValidationError('Vous ne pouvez pas retirer vos propres accès.')
        if not self.instance and not attrs.get('password'):
            raise serializers.ValidationError({'password': 'Un mot de passe est obligatoire.'})
        if 'password' in attrs:
            candidate = User(username=attrs.get('username', getattr(self.instance, 'username', '')),
                             email=attrs.get('email', getattr(self.instance, 'email', '')),
                             first_name=attrs.get('first_name', ''), last_name=attrs.get('last_name', ''))
            try:
                validate_password(attrs['password'], candidate)
            except DjangoValidationError as exc:
                raise serializers.ValidationError({'password': exc.messages}) from exc
        return attrs

    def save_certificates(self, instance, uploads, removed_ids):
        for document in instance.certificate_documents.filter(pk__in=removed_ids):
            storage, name = document.file.storage, document.file.name
            document.delete()
            transaction.on_commit(lambda storage=storage, name=name: storage.delete(name), robust=True)
        for upload in uploads:
            name = Path(upload.name).name
            upload.name = f'{uuid4().hex}{Path(name).suffix.lower()}'
            TechnicianCertificate.objects.create(user=instance, file=upload, name=name)

    @transaction.atomic
    def create(self, validated_data):
        uploads = validated_data.pop('certificate_files', [])
        validated_data.pop('remove_certificate_ids', None)
        instance = User.objects.create_user(**validated_data)
        if instance.role == User.Role.TECHNICIAN:
            instance.employee_number = self.next_employee_number(instance)
            instance.save(update_fields=['employee_number'])
        self.save_photo_from_cv(instance)
        self.save_certificates(instance, uploads, [])
        return instance

    def next_employee_number(self, instance):
        year = timezone.localdate(instance.date_joined).year
        TechnicianSequence.objects.get_or_create(year=year)
        sequence = TechnicianSequence.objects.select_for_update().get(year=year)
        if sequence.last_number >= 99999:
            raise serializers.ValidationError('Le nombre maximum de matricules pour cette année est atteint.')
        sequence.last_number += 1
        sequence.save(update_fields=['last_number'])
        return f'CP-{year}-{sequence.last_number:05d}'

    def save_photo_from_cv(self, instance):
        if instance.photo or not instance.cv:
            return
        with instance.cv.open('rb') as upload:
            photo_data = extract_cv_photo(upload)
        if photo_data:
            instance.photo.save('photo-from-cv.png', ContentFile(photo_data), save=True)

    @transaction.atomic
    def update(self, instance, validated_data):
        uploads = validated_data.pop('certificate_files', [])
        removed_ids = validated_data.pop('remove_certificate_ids', [])
        password = validated_data.pop('password', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if password:
            instance.set_password(password)
        instance.save()
        if instance.role == User.Role.TECHNICIAN and not instance.employee_number:
            instance.employee_number = self.next_employee_number(instance)
            instance.save(update_fields=['employee_number'])
        self.save_photo_from_cv(instance)
        self.save_certificates(instance, uploads, removed_ids)
        return instance


class ProjectSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    manager_name = serializers.CharField(required=False, allow_blank=True, max_length=200)
    technician_names = serializers.SerializerMethodField()
    technician_labor_cost = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'client', 'client_name', 'site', 'description', 'project_manager',
                  'manager_name', 'technicians', 'technician_names', 'hourly_rate',
                  'holiday_billing_day_rate', 'technician_hourly_rate', 'holiday_day_rate',
                  'technician_labor_cost', 'budget',
                  'purchase_order', 'status', 'created_at']
        read_only_fields = ['created_at']

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request and request.user.effective_role in [User.Role.TECHNICIAN, User.Role.PROJECT_MANAGER]:
            for field in ['hourly_rate', 'holiday_billing_day_rate', 'technician_hourly_rate', 'holiday_day_rate', 'technician_labor_cost', 'budget']:
                fields.pop(field)
        return fields

    def get_technician_names(self, obj):
        return [u.get_full_name() or u.username for u in obj.technicians.all()]

    def get_technician_labor_cost(self, obj):
        entries = getattr(obj, 'cost_entries', None)
        if entries is None:
            entries = obj.time_entries.filter(status__in=['APPROVED', 'INVOICED']).select_related('technician')
        holidays = getattr(self, '_holiday_dates', None)
        if holidays is None:
            holidays = set(PublicHoliday.objects.values_list('date', flat=True))
            self._holiday_dates = holidays

        total = Decimal('0.00')
        holiday_workdays = set()
        for entry in entries:
            work_date = timezone.localtime(entry.start).date()
            if work_date in holidays:
                holiday_workdays.add((entry.technician_id, work_date))
            else:
                total += entry.hours * obj.technician_hourly_rate
        total += obj.holiday_day_rate * len(holiday_workdays)
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def validate(self, attrs):
        client = attrs.get('client', getattr(self.instance, 'client', None))
        manager_name = attrs.get('manager_name', getattr(self.instance, 'manager_name', '')).strip()
        if self.instance and 'manager_name' in attrs and 'project_manager' not in attrs:
            if manager_name != self.instance.manager_name:
                attrs['project_manager'] = None
        manager = attrs.get('project_manager', getattr(self.instance, 'project_manager', None))
        if not client or not client.is_active:
            raise serializers.ValidationError({'client': 'Sélectionnez un client actif.'})
        if manager and (not manager.is_active or manager.role != User.Role.PROJECT_MANAGER or manager.client_id != client.pk):
            raise serializers.ValidationError({'project_manager': 'Sélectionnez un chef de projet actif de ce client.'})
        if not manager_name and manager:
            manager_name = manager.get_full_name() or manager.username
        if not manager_name:
            raise serializers.ValidationError({'manager_name': 'Saisissez le nom du chef de projet client.'})
        attrs['manager_name'] = manager_name
        for technician in attrs.get('technicians', []):
            if technician.role != User.Role.TECHNICIAN or not technician.is_active:
                raise serializers.ValidationError({'technicians': 'Seuls les techniciens actifs peuvent être affectés.'})
        for field in ['hourly_rate', 'holiday_billing_day_rate', 'technician_hourly_rate', 'holiday_day_rate', 'budget']:
            if attrs.get(field, 0) < 0:
                raise serializers.ValidationError({field: 'Le montant doit être positif ou nul.'})
        if self.instance and client.pk != self.instance.client_id and self.instance.time_entries.exists():
            raise serializers.ValidationError({'client': 'Un projet avec des pointages ne peut pas changer de client.'})
        if self.instance and client.pk != self.instance.client_id and self.instance.access_user_id:
            raise serializers.ValidationError({'client': 'Un projet avec un accès client ne peut pas changer de client.'})
        return attrs


class PublicHolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicHoliday
        fields = ['id', 'name', 'date']


class TimeEntryEventSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()

    class Meta:
        model = TimeEntryEvent
        fields = ['id', 'actor_name', 'status', 'comment', 'created_at']

    def get_actor_name(self, obj):
        return obj.actor.get_full_name() or obj.actor.username


class TimeEntrySerializer(serializers.ModelSerializer):
    technician_name = serializers.SerializerMethodField()
    project_name = serializers.CharField(source='project.name', read_only=True)
    client_name = serializers.CharField(source='project.client.name', read_only=True)
    hours = serializers.DecimalField(max_digits=7, decimal_places=2, read_only=True)
    events = TimeEntryEventSerializer(many=True, read_only=True)

    class Meta:
        model = TimeEntry
        fields = ['id', 'technician', 'technician_name', 'project', 'project_name', 'client_name',
                  'start', 'end', 'break_minutes', 'description', 'hours', 'status',
                  'reviewed_by', 'reviewed_at', 'rejection_reason', 'events']
        read_only_fields = ['technician', 'status', 'reviewed_by', 'reviewed_at', 'rejection_reason']

    def get_technician_name(self, obj):
        return obj.technician.get_full_name() or obj.technician.username

    def validate(self, attrs):
        user = self.context['request'].user
        if user.effective_role != User.Role.TECHNICIAN:
            raise serializers.ValidationError('Seul le technicien saisit ses propres heures.')
        if self.instance and (self.instance.technician_id != user.pk or self.instance.status not in ['DRAFT', 'REJECTED']):
            raise serializers.ValidationError('Ce pointage ne peut plus être modifié.')
        project = attrs.get('project', getattr(self.instance, 'project', None))
        if not project or project.status != 'ACTIVE' or not project.client.is_active or not project.technicians.filter(pk=user.pk).exists():
            raise serializers.ValidationError({'project': 'Choisissez un projet actif auquel vous êtes affecté.'})
        start = attrs.get('start', getattr(self.instance, 'start', None))
        end = attrs.get('end', getattr(self.instance, 'end', None))
        pause = attrs.get('break_minutes', getattr(self.instance, 'break_minutes', 0))
        if not start or not end or end <= start or end - start > timedelta(hours=24):
            raise serializers.ValidationError({'end': 'La durée doit être comprise entre 1 minute et 24 heures.'})
        if end > timezone.now() + timedelta(minutes=1):
            raise serializers.ValidationError({'end': 'Vous ne pouvez pas déclarer des heures futures.'})
        if pause < 0 or (end - start).total_seconds() - pause * 60 < 60:
            raise serializers.ValidationError({'break_minutes': 'La pause doit laisser au moins une minute de travail.'})
        # Caller holds a lock on this technician, serializing overlap checks on MySQL.
        overlap = TimeEntry.objects.filter(technician=user, start__lt=end, end__gt=start)
        if self.instance:
            overlap = overlap.exclude(pk=self.instance.pk)
        if overlap.exists():
            raise serializers.ValidationError('Ces heures chevauchent un autre pointage.')
        return attrs

    def create(self, validated_data):
        entry = super().create({**validated_data, 'technician': self.context['request'].user})
        TimeEntryEvent.objects.create(entry=entry, actor=self.context['request'].user, status=entry.status)
        return entry

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        TimeEntryEvent.objects.create(entry=instance, actor=self.context['request'].user,
                                      status=instance.status, comment='Pointage corrigé.')
        return instance


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'invoice', 'amount', 'date', 'method', 'reference', 'created_at']
        read_only_fields = ['created_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Le paiement doit être supérieur à zéro.')
        return value

    def validate_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError('La date du paiement ne peut pas être future.')
        return value


class InvoiceLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLine
        fields = ['id', 'time_entry', 'technician_name', 'description', 'work_date', 'hours', 'rate', 'amount']


class InvoiceSerializer(serializers.ModelSerializer):
    lines = InvoiceLineSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    paid = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    balance = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    number = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Invoice
        fields = ['id', 'number', 'project', 'project_name', 'client_name', 'billing_address',
                  'purchase_order', 'currency', 'tax_percent', 'subtotal', 'tax_amount', 'total',
                  'issued_at', 'due_date', 'paid', 'balance', 'status', 'lines', 'payments']
        read_only_fields = fields


class InvoiceCreateSerializer(serializers.Serializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    entry_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=False)
    due_date = serializers.DateField()
    tax_percent = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100, default=0)

    def validate_due_date(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError('L’échéance ne peut pas être dans le passé.')
        return value

    def validate_entry_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Chaque pointage doit apparaître une seule fois.')
        return value
