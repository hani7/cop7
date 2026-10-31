from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from collections import defaultdict

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from .access import projects_for, require_role
from .models import Invoice, InvoiceLine, Payment, Project, PublicHoliday, TimeEntry, TimeEntryEvent, User


@transaction.atomic
def transition_entry(entry_id, user, action, reason=''):
    entry = TimeEntry.objects.select_for_update().get(pk=entry_id)
    if action == 'submit':
        require_role(user, User.Role.TECHNICIAN)
        if entry.technician_id != user.pk:
            raise PermissionDenied()
        if entry.status not in ['DRAFT', 'REJECTED']:
            raise ValidationError('Ce pointage est déjà soumis ou validé.')
        if entry.project.status != 'ACTIVE' or not entry.project.client.is_active or not entry.project.technicians.filter(pk=user.pk).exists():
            raise ValidationError('Ce projet ne permet plus la soumission de vos pointages.')
        entry.status = 'SUBMITTED'
        entry.reviewed_by = None
        entry.reviewed_at = None
        entry.rejection_reason = ''
    else:
        require_role(user, User.Role.PROJECT_MANAGER)
        if not projects_for(user).filter(pk=entry.project_id).exists():
            raise PermissionDenied()
        if entry.status != 'SUBMITTED':
            raise ValidationError('Seul un pointage soumis peut être validé ou refusé.')
        if action not in ['approve', 'reject']:
            raise ValidationError('Action inconnue.')
        if action == 'reject' and not reason.strip():
            raise ValidationError({'reason': 'Indiquez le motif du refus.'})
        entry.status = 'APPROVED' if action == 'approve' else 'REJECTED'
        entry.reviewed_by = user
        entry.reviewed_at = timezone.now()
        entry.rejection_reason = reason.strip() if action == 'reject' else ''
    entry.save()
    TimeEntryEvent.objects.create(entry=entry, actor=user, status=entry.status, comment=entry.rejection_reason)
    return entry


@transaction.atomic
def create_invoice(user, project, entry_ids, due_date, tax_percent, date_from=None, date_to=None, purchase_order=''):
    require_role(user, User.Role.ADMIN)
    project = Project.objects.select_for_update().get(pk=project.pk)
    entries = list(TimeEntry.objects.select_for_update().filter(pk__in=entry_ids).order_by('pk'))
    if date_from:
        entries = [entry for entry in entries if timezone.localtime(entry.start).date() >= date_from]
    if date_to:
        entries = [entry for entry in entries if timezone.localtime(entry.start).date() <= date_to]
    if len(entries) != len(entry_ids) or any(e.project_id != project.pk or e.status != 'APPROVED' for e in entries):
        raise ValidationError('Choisissez uniquement des pointages validés et non facturés de ce projet.')
    if not entries:
        raise ValidationError('Sélectionnez au moins un pointage.')
    holiday_dates = {
        timezone.localtime(entry.start).date()
        for entry in entries
    }
    holiday_dates = set(PublicHoliday.objects.filter(date__in=holiday_dates).values_list('date', flat=True))
    holiday_groups = defaultdict(list)
    amounts_by_entry = {}
    rates_by_entry = {}
    for entry in entries:
        work_date = timezone.localtime(entry.start).date()
        if work_date in holiday_dates:
            holiday_groups[(entry.technician_id, work_date)].append(entry)
        else:
            amount = (entry.hours * project.hourly_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            amounts_by_entry[entry.pk] = amount
            rates_by_entry[entry.pk] = project.hourly_rate
    for group_entries in holiday_groups.values():
        total_hours = sum((entry.hours for entry in group_entries), Decimal('0.00'))
        day_amount = project.holiday_billing_day_rate
        allocated = Decimal('0.00')
        for index, entry in enumerate(group_entries):
            amount = day_amount - allocated if index == len(group_entries) - 1 else (
                day_amount * entry.hours / total_hours
            ).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            allocated += amount
            amounts_by_entry[entry.pk] = amount
            rates_by_entry[entry.pk] = (amount / entry.hours).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    amounts = [amounts_by_entry[entry.pk] for entry in entries]
    subtotal = sum(amounts, Decimal('0.00'))
    tax = (subtotal * tax_percent / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    if subtotal <= 0 or subtotal + tax >= Decimal('1000000000000'):
        raise ValidationError('Vérifiez le tarif horaire : le total doit être positif et inférieur à 1 000 milliards.')
    invoice = Invoice.objects.create(
        project=project, project_name=project.name, client_name=project.client.name,
        billing_address=project.client.billing_address, purchase_order=purchase_order or project.purchase_order,
        currency=settings.APP_CURRENCY, tax_percent=tax_percent, subtotal=subtotal,
        tax_amount=tax, total=subtotal + tax, due_date=due_date, created_by=user,
    )
    for entry, amount in zip(entries, amounts):
        InvoiceLine.objects.create(
            invoice=invoice, time_entry=entry, technician_name=entry.technician.get_full_name() or entry.technician.username,
            description=entry.description, work_date=timezone.localtime(entry.start).date(),
            hours=entry.hours, rate=rates_by_entry[entry.pk], amount=amount,
        )
        entry.status = 'INVOICED'
        entry.save(update_fields=['status'])
        TimeEntryEvent.objects.create(entry=entry, actor=user, status='INVOICED', comment=invoice.number)
    return invoice


@transaction.atomic
def record_payment(user, **data):
    require_role(user, User.Role.ADMIN)
    invoice = Invoice.objects.select_for_update().get(pk=data['invoice'].pk)
    if data['amount'] > invoice.balance:
        raise ValidationError({'amount': 'Le paiement dépasse le solde de la facture.'})
    if data['date'] < timezone.localtime(invoice.issued_at).date():
        raise ValidationError({'date': 'Le paiement ne peut pas précéder la facture.'})
    return Payment.objects.create(**{**data, 'invoice': invoice}, created_by=user)
