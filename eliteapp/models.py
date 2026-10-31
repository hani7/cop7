from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import F, Q


class Client(models.Model):
    name = models.CharField('Société', max_length=160)
    contact_name = models.CharField('Contact', max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField('Téléphone', max_length=40, blank=True)
    rc = models.CharField('RC', max_length=40, blank=True)
    nif = models.CharField('NIF', max_length=40, blank=True)
    article_number = models.CharField('N° article', max_length=40, blank=True)
    nis = models.CharField('NIS', max_length=40, blank=True)
    billing_address = models.TextField('Adresse de facturation', blank=True)
    start_work_date = models.DateField('Date de début de travail', null=True, blank=True)
    logo = models.FileField('Logo', upload_to='client-logos/', blank=True)
    is_active = models.BooleanField('Actif', default=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class AppUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('role', 'ADMIN')
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrateur'
        SUPERVISOR = 'SUPERVISOR', 'Superviseur interne'
        TECHNICIAN = 'TECHNICIAN', 'Technicien'
        PROJECT_MANAGER = 'PROJECT_MANAGER', 'Chef de projet client'

    role = models.CharField(max_length=20, choices=Role, default=Role.TECHNICIAN)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, null=True, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    birth_date = models.DateField('Date de naissance', null=True, blank=True)
    assignment_date = models.DateField('Date d’affectation', null=True, blank=True)
    address = models.TextField('Adresse', blank=True, max_length=2000)
    experience = models.TextField('Expérience professionnelle', blank=True, max_length=20000)
    certificates = models.TextField('Certificats', blank=True, max_length=10000)
    cv = models.FileField('CV', upload_to='technician-cvs/', blank=True)
    photo = models.FileField('Photo de profil', upload_to='technician-photos/', blank=True)
    specialty = models.CharField('Spécialité', max_length=120, blank=True)
    employee_number = models.CharField('Matricule', max_length=40, blank=True)
    hourly_cost = models.DecimalField('Coût horaire', max_digits=10, decimal_places=2, default=0)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    objects = AppUserManager()

    @property
    def effective_role(self):
        return self.Role.ADMIN if self.is_superuser else self.role

    class Meta:
        ordering = ['first_name', 'last_name', 'username']
        constraints = [
            models.CheckConstraint(condition=Q(hourly_cost__gte=0), name='positive_hourly_cost'),
            models.CheckConstraint(
                condition=(Q(role='PROJECT_MANAGER', client__isnull=False)
                           | (~Q(role='PROJECT_MANAGER') & Q(client__isnull=True))),
                name='client_required_for_project_manager',
            ),
        ]


class TechnicianSequence(models.Model):
    year = models.PositiveSmallIntegerField(primary_key=True)
    last_number = models.PositiveIntegerField(default=0)


class TechnicianSpecialty(models.Model):
    name = models.CharField('Spécialité', max_length=120, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Spécialité technicien'
        verbose_name_plural = 'Spécialités techniciens'

    def __str__(self):
        return self.name


class TechnicianCertificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificate_documents')
    file = models.FileField('Certificat', upload_to='technician-certificates/', max_length=255)
    name = models.CharField('Nom du fichier', max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'pk']


class Project(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'En cours'
        COMPLETED = 'COMPLETED', 'Terminé'

    name = models.CharField('Projet', max_length=160)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='projects')
    site = models.CharField('Site industriel', max_length=200)
    description = models.TextField(blank=True)
    manager_name = models.CharField('Chef de projet client', max_length=200, blank=True, default='')
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='managed_projects',
        limit_choices_to={'role': 'PROJECT_MANAGER'}, null=True, blank=True,
    )
    access_user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='access_project',
        limit_choices_to={'role': 'PROJECT_MANAGER'}, null=True, blank=True,
    )
    technicians = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='assigned_projects', blank=True,
        limit_choices_to={'role': 'TECHNICIAN'},
    )
    hourly_rate = models.DecimalField('Tarif client / heure', max_digits=10, decimal_places=2)
    holiday_billing_day_rate = models.DecimalField('Tarif facture journée fériée', max_digits=10, decimal_places=2, default=0)
    technician_hourly_rate = models.DecimalField('Tarif technicien / heure', max_digits=10, decimal_places=2, default=0)
    holiday_day_rate = models.DecimalField('Tarif technicien journée fériée', max_digits=10, decimal_places=2, default=0)
    budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    purchase_order = models.CharField('Bon de commande', max_length=100, blank=True)
    status = models.CharField(max_length=12, choices=Status, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(condition=Q(hourly_rate__gte=0), name='positive_project_rate'),
            models.CheckConstraint(condition=Q(holiday_billing_day_rate__gte=0), name='positive_project_holiday_billing_rate'),
            models.CheckConstraint(condition=Q(technician_hourly_rate__gte=0), name='positive_technician_project_rate'),
            models.CheckConstraint(condition=Q(holiday_day_rate__gte=0), name='positive_project_holiday_rate'),
            models.CheckConstraint(condition=Q(budget__gte=0), name='positive_project_budget'),
        ]

    def __str__(self):
        return self.name


class PublicHoliday(models.Model):
    name = models.CharField('Nom du jour férié', max_length=120)
    date = models.DateField('Date', unique=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f'{self.name} ({self.date})'


class TimeEntry(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Brouillon'
        SUBMITTED = 'SUBMITTED', 'À valider'
        APPROVED = 'APPROVED', 'Validé'
        REJECTED = 'REJECTED', 'Refusé'
        INVOICED = 'INVOICED', 'Facturé'

    technician = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='time_entries')
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='time_entries')
    start = models.DateTimeField('Début')
    end = models.DateTimeField('Fin')
    break_minutes = models.PositiveIntegerField('Pause (minutes)', default=0)
    description = models.TextField('Travaux réalisés')
    status = models.CharField(max_length=12, choices=Status, default=Status.DRAFT)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='reviews',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def hours(self):
        seconds = Decimal(str((self.end - self.start).total_seconds()))
        return ((seconds - self.break_minutes * 60) / 3600).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    class Meta:
        ordering = ['-start']
        constraints = [models.CheckConstraint(condition=Q(end__gt=F('start')), name='time_end_after_start')]
        indexes = [models.Index(fields=['technician', 'start', 'end'])]


class TimeEntryEvent(models.Model):
    entry = models.ForeignKey(TimeEntry, on_delete=models.PROTECT, related_name='events')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.CharField(max_length=12, choices=TimeEntry.Status)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']


class Invoice(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='invoices')
    client_name = models.CharField(max_length=160)
    billing_address = models.TextField(blank=True)
    project_name = models.CharField(max_length=160)
    purchase_order = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=3)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2)
    total = models.DecimalField(max_digits=14, decimal_places=2)
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField('Échéance')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    @property
    def number(self):
        return f'FAC-{self.issued_at.year}-{self.pk:05d}'

    @property
    def paid(self):
        return sum((payment.amount for payment in self.payments.all()), Decimal('0.00'))

    @property
    def balance(self):
        return self.total - self.paid

    @property
    def status(self):
        if self.balance <= 0:
            return 'PAID'
        return 'PARTIAL' if self.paid else 'UNPAID'

    class Meta:
        ordering = ['-issued_at']


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='lines')
    time_entry = models.OneToOneField(TimeEntry, on_delete=models.PROTECT, related_name='invoice_line')
    technician_name = models.CharField(max_length=160)
    description = models.TextField()
    work_date = models.DateField()
    hours = models.DecimalField(max_digits=7, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=14, decimal_places=2)


class Payment(models.Model):
    class Method(models.TextChoices):
        TRANSFER = 'TRANSFER', 'Virement'
        CASH = 'CASH', 'Espèces'
        CHECK = 'CHECK', 'Chèque'

    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateField()
    method = models.CharField(max_length=12, choices=Method, default=Method.TRANSFER)
    reference = models.CharField(max_length=160, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']
        constraints = [models.CheckConstraint(condition=Q(amount__gt=0), name='positive_payment')]


class TechnicianPayment(models.Model):
    class Method(models.TextChoices):
        TRANSFER = 'TRANSFER', 'Virement'
        CASH = 'CASH', 'Espèces'
        CHECK = 'CHECK', 'Chèque'

    technician = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='technician_payments')
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateField()
    method = models.CharField(max_length=12, choices=Method, default=Method.TRANSFER)
    reference = models.CharField(max_length=160, blank=True)
    note = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_technician_payments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']
        constraints = [models.CheckConstraint(condition=Q(amount__gt=0), name='positive_technician_payment')]
