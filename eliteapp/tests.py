from datetime import timedelta
from decimal import Decimal
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
import pymupdf
from rest_framework.test import APIClient, APITestCase

from .models import Client, Invoice, Project, PublicHoliday, TimeEntry, TimeEntryEvent

User = get_user_model()


class ProjectAccessTests(APITestCase):
    password = 'Client-Access-839!Safe'

    @classmethod
    def setUpTestData(cls):
        cls.company = Client.objects.create(name='Client commun')
        cls.admin = User.objects.create_user('access-admin', role='ADMIN', password=cls.password)
        cls.tech = User.objects.create_user('access-tech', role='TECHNICIAN', password=cls.password)
        cls.account = User.objects.create_user('project-client', role='PROJECT_MANAGER',
                                               client=cls.company, password=cls.password)
        cls.manager = User.objects.create_user('legacy-manager', role='PROJECT_MANAGER',
                                               client=cls.company, password=cls.password)
        cls.project = Project.objects.create(name='Projet A', client=cls.company, hourly_rate='45',
                                              access_user=cls.account, project_manager=cls.manager)
        cls.project.technicians.add(cls.tech)
        # Even an extra manager assignment must not broaden a dedicated account's access.
        cls.other_project = Project.objects.create(name='Projet B', client=cls.company, hourly_rate='50',
                                                    project_manager=cls.account)
        start = timezone.now() - timedelta(days=2)
        cls.entry = TimeEntry.objects.create(technician=cls.tech, project=cls.project, start=start,
                                             end=start + timedelta(hours=2), description='Travaux', status='SUBMITTED')
        cls.other_entry = TimeEntry.objects.create(technician=cls.tech, project=cls.other_project,
                                                   start=start + timedelta(days=1), end=start + timedelta(days=1, hours=2),
                                                   description='Autres travaux', status='SUBMITTED')

    def setUp(self):
        cache.clear()

    def test_admin_creates_distinct_project_credentials_and_reads_no_password(self):
        self.client.force_authenticate(self.admin)
        path = f'/api/projects/{self.other_project.pk}/access/'
        self.assertFalse(self.client.get(path).data['configured'])
        response = self.client.post(path, {'username': 'client-projet-b', 'password': self.password,
                                           'role': 'ADMIN', 'client': None}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.other_project.refresh_from_db()
        account = self.other_project.access_user
        self.assertNotEqual(account.pk, self.account.pk)
        self.assertEqual(account.role, 'PROJECT_MANAGER')
        self.assertEqual(account.client, self.company)
        self.assertTrue(account.check_password(self.password))
        self.assertNotEqual(account.password, self.password)
        self.assertEqual(response.data['login_path'], '/project/login')
        self.assertNotIn('password', response.data)
        self.assertNotIn('password', self.client.get(path).data)

    def test_project_login_requires_csrf_and_a_dedicated_account(self):
        client = APIClient(enforce_csrf_checks=True)
        payload = {'username': self.account.username, 'password': self.password}
        self.assertEqual(client.post('/api/auth/project-login/', payload).status_code, 403)
        token = client.get('/api/auth/session/').data['csrfToken']
        for user in [self.admin, self.tech, self.manager]:
            response = client.post('/api/auth/project-login/', {'username': user.username, 'password': self.password},
                                   HTTP_X_CSRFTOKEN=token)
            self.assertEqual(response.status_code, 403, response.data)
            self.assertIsNone(client.get('/api/auth/session/').data['user'])
        response = client.post('/api/auth/project-login/', payload, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['user']['project_access'], {'id': self.project.pk, 'name': 'Projet A'})
        self.assertEqual(client.get('/api/projects/').data['count'], 1)

    def test_project_account_can_approve_only_its_own_project(self):
        self.client.force_authenticate(self.account)
        projects = self.client.get('/api/projects/').data['results']
        self.assertEqual([project['id'] for project in projects], [self.project.pk])
        self.assertNotIn('hourly_rate', projects[0])
        self.assertEqual([entry['id'] for entry in self.client.get('/api/time-entries/').data['results']], [self.entry.pk])
        self.assertEqual(self.client.get(f'/api/projects/{self.other_project.pk}/').status_code, 404)
        self.assertEqual(self.client.get(f'/api/time-entries/{self.other_entry.pk}/').status_code, 404)
        for action in ['approve', 'reject']:
            self.assertEqual(self.client.post(f'/api/time-entries/{self.other_entry.pk}/{action}/', {'reason': 'Refus'}).status_code, 404)
        self.assertEqual(self.client.post(f'/api/time-entries/{self.entry.pk}/approve/').status_code, 200)
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.status, 'APPROVED')
        self.assertEqual(self.entry.reviewed_by, self.account)
        self.assertTrue(self.entry.events.filter(actor=self.account, status='APPROVED').exists())
        for path in ['/api/invoices/', '/api/payments/']:
            self.assertEqual(self.client.get(path).status_code, 403)
        self.assertEqual(self.client.patch(f'/api/projects/{self.project.pk}/', {'name': 'Changed'}).status_code, 403)

    def test_project_account_sees_only_assigned_technicians(self):
        self.client.force_authenticate(self.account)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([user['id'] for user in response.data['results']], [self.tech.pk])

    def test_project_account_can_reject_with_reason_but_cannot_see_drafts(self):
        self.client.force_authenticate(self.account)
        path = f'/api/time-entries/{self.entry.pk}/reject/'
        self.assertEqual(self.client.post(path, {'reason': ''}).status_code, 400)
        self.assertEqual(self.client.post(path, {'reason': 'Heures à corriger'}).status_code, 200)
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.rejection_reason, 'Heures à corriger')
        self.assertEqual(self.entry.reviewed_by, self.account)
        self.entry.status = 'DRAFT'
        self.entry.save(update_fields=['status'])
        self.assertEqual(self.client.get('/api/time-entries/').data['count'], 0)

    def test_only_admin_manages_access_and_invalid_credentials_do_not_create_users(self):
        path = f'/api/projects/{self.other_project.pk}/access/'
        self.assertIn(self.client.get(path).status_code, [401, 403])
        supervisor = User.objects.create_user('access-supervisor', role='SUPERVISOR')
        for user in [self.tech, self.account, self.manager, supervisor]:
            self.client.force_authenticate(user)
            self.assertEqual(self.client.get(path).status_code, 403)
            self.assertEqual(self.client.post(path, {'username': 'not-created', 'password': self.password}).status_code, 403)
        self.client.force_authenticate(self.admin)
        count = User.objects.count()
        for payload in [{'username': 'new-client'}, {'username': 'new-client', 'password': '123'},
                        {'username': self.account.username, 'password': self.password}]:
            self.assertEqual(self.client.post(path, payload).status_code, 400)
        self.assertEqual(User.objects.count(), count)
        self.other_project.refresh_from_db()
        self.assertIsNone(self.other_project.access_user_id)

    def test_reset_password_and_disable_project_access(self):
        client = APIClient()
        self.assertEqual(client.post('/api/auth/project-login/', {'username': self.account.username, 'password': self.password}).status_code, 200)
        self.client.force_authenticate(self.admin)
        path = f'/api/projects/{self.project.pk}/access/'
        new_password = 'New-Project-Access-934!'
        self.assertEqual(self.client.post(path, {'password': new_password}).status_code, 200)
        self.assertIsNone(client.get('/api/auth/session/').data['user'])
        self.assertEqual(client.post('/api/auth/project-login/', {'username': self.account.username, 'password': self.password}).status_code, 400)
        self.assertEqual(client.post('/api/auth/project-login/', {'username': self.account.username, 'password': new_password}).status_code, 200)
        self.assertEqual(self.client.post(path, {'is_active': False}).status_code, 200)
        self.assertIsNone(client.get('/api/auth/session/').data['user'])
        self.assertEqual(client.post('/api/auth/project-login/', {'username': self.account.username, 'password': new_password}).status_code, 400)

    def test_inactive_client_blocks_login_and_project_access(self):
        self.company.is_active = False
        self.company.save(update_fields=['is_active'])
        response = self.client.post('/api/auth/project-login/', {'username': self.account.username, 'password': self.password})
        self.assertEqual(response.status_code, 403)
        self.client.force_authenticate(self.account)
        self.assertEqual(self.client.get('/api/projects/').data['count'], 0)
        self.assertEqual(self.client.post(f'/api/time-entries/{self.entry.pk}/approve/').status_code, 404)

    def test_admin_can_delete_unlinked_project_but_history_is_protected(self):
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.delete(f'/api/projects/{self.other_project.pk}/').status_code, 204)
        self.other_project.refresh_from_db()
        self.assertIsNotNone(self.other_project.deleted_at)
        deletable = Project.objects.create(name='Projet supprimable', client=self.company, hourly_rate='10')
        response = self.client.delete(f'/api/projects/{deletable.pk}/')
        self.assertEqual(response.status_code, 204)
        deletable.refresh_from_db()
        self.assertIsNotNone(deletable.deleted_at)
        self.assertEqual(self.client.post(f'/api/trash/{deletable.pk}/restore/?type=projects').status_code, 200)
        deletable.refresh_from_db()
        self.assertIsNone(deletable.deleted_at)

    def test_admin_can_create_a_manual_time_entry_for_an_assigned_technician(self):
        self.client.force_authenticate(self.admin)
        start = timezone.now() - timedelta(hours=3)
        response = self.client.post('/api/time-entries/', {
            'technician': self.tech.pk, 'project': self.project.pk,
            'start': start.isoformat(), 'end': (start + timedelta(hours=1)).isoformat(),
            'break_minutes': 0, 'description': 'Pointage saisi manuellement',
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['technician'], self.tech.pk)
        self.assertEqual(response.data['status'], 'DRAFT')

    def test_only_admin_can_add_technician_specialties(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post('/api/technician-specialties/', {'name': '  soudeur  '}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['name'], 'SOUDEUR')
        self.assertEqual(self.client.get('/api/technician-specialties/').data['results'][0]['name'], 'SOUDEUR')
        assigned = self.client.patch(f'/api/users/{self.tech.pk}/', {'specialty': 'SOUDEUR'}, format='json')
        self.assertEqual(assigned.status_code, 200, assigned.data)
        self.tech.refresh_from_db()
        self.assertEqual(self.tech.specialty, 'SOUDEUR')
        renamed = self.client.patch(f'/api/technician-specialties/{response.data["id"]}/', {'name': 'Electricien'}, format='json')
        self.assertEqual(renamed.status_code, 200, renamed.data)
        self.tech.refresh_from_db()
        self.assertEqual(self.tech.specialty, 'ELECTRICIEN')
        self.client.force_authenticate(self.tech)
        self.assertEqual(self.client.get('/api/technician-specialties/').status_code, 403)
        self.assertEqual(self.client.post('/api/technician-specialties/', {'name': 'Peintre'}).status_code, 403)


class WorkflowTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Client.objects.create(name='Industrie Alpha', billing_address='Site Alpha')
        cls.other_company = Client.objects.create(name='Industrie Beta')
        cls.admin = User.objects.create_user('admin', password='Test-Strong-839!', role='ADMIN')
        cls.supervisor = User.objects.create_user('supervisor', role='SUPERVISOR')
        cls.tech = User.objects.create_user('tech', first_name='Amine', role='TECHNICIAN', hourly_cost='18.00')
        cls.other_tech = User.objects.create_user('other-tech', role='TECHNICIAN')
        cls.manager = User.objects.create_user('manager', role='PROJECT_MANAGER', client=cls.company)
        cls.same_client_manager = User.objects.create_user('manager-2', role='PROJECT_MANAGER', client=cls.company)
        cls.other_manager = User.objects.create_user('other-manager', role='PROJECT_MANAGER', client=cls.other_company)
        cls.project = Project.objects.create(name='Maintenance', client=cls.company, project_manager=cls.manager,
                                             site='Atelier A', hourly_rate='45.00', budget='5000')
        cls.project.technicians.add(cls.tech)
        cls.other_project = Project.objects.create(name='Autre site', client=cls.other_company,
                                                   project_manager=cls.other_manager, site='B', hourly_rate='60')
        cls.other_project.technicians.add(cls.other_tech)
        cls.start = (timezone.now() - timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)

    def setUp(self):
        cache.clear()

    def sign_in(self, user):
        self.client.force_authenticate(user)

    def payload(self, **overrides):
        return {'project': self.project.pk, 'start': self.start.isoformat(),
                'end': (self.start + timedelta(hours=9)).isoformat(), 'break_minutes': 60,
                'description': 'Maintenance préventive', **overrides}

    def entry(self, status='DRAFT', **overrides):
        return TimeEntry.objects.create(technician=self.tech, project=self.project, start=self.start,
                                       end=self.start + timedelta(hours=9), break_minutes=60,
                                       description='Maintenance préventive', status=status, **overrides)

    def issue(self, entry):
        self.sign_in(self.admin)
        response = self.client.post('/api/invoices/', {'project': self.project.pk, 'entry_ids': [entry.pk],
                                    'due_date': str(timezone.localdate() + timedelta(days=30)), 'tax_percent': '20.00'}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def test_complete_approval_invoice_and_partial_payment_workflow(self):
        self.sign_in(self.tech)
        response = self.client.post('/api/time-entries/', self.payload(), format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['hours'], '8.00')
        entry_id = response.data['id']
        self.assertEqual(self.client.post(f'/api/time-entries/{entry_id}/submit/').status_code, 200)
        self.sign_in(self.manager)
        self.assertEqual(self.client.post(f'/api/time-entries/{entry_id}/approve/').status_code, 200)
        entry = TimeEntry.objects.get(pk=entry_id)
        self.assertEqual(entry.reviewed_by, self.manager)
        invoice = self.issue(entry)
        self.assertEqual(invoice['subtotal'], '360.00')
        self.assertEqual(invoice['tax_amount'], '72.00')
        self.assertEqual(invoice['total'], '432.00')
        entry.refresh_from_db()
        self.assertEqual(entry.status, 'INVOICED')
        for amount in ['100.00', '332.00']:
            response = self.client.post('/api/payments/', {'invoice': invoice['id'], 'amount': amount,
                                        'date': str(timezone.localdate()), 'method': 'TRANSFER'}, format='json')
            self.assertEqual(response.status_code, 201, response.data)
        invoice = self.client.get(f"/api/invoices/{invoice['id']}/").data
        self.assertEqual(invoice['status'], 'PAID')
        self.assertEqual(invoice['balance'], '0.00')
        self.assertEqual(list(TimeEntryEvent.objects.filter(entry_id=entry_id).values_list('status', flat=True)),
                         ['DRAFT', 'SUBMITTED', 'APPROVED', 'INVOICED'])

    def test_client_manager_is_scoped_to_assigned_projects_not_just_company(self):
        entry = self.entry('SUBMITTED')
        for manager in [self.other_manager, self.same_client_manager]:
            self.sign_in(manager)
            self.assertEqual(self.client.get('/api/time-entries/').data['count'], 0)
            self.assertEqual(self.client.post(f'/api/time-entries/{entry.pk}/approve/').status_code, 404)
        self.sign_in(self.manager)
        self.assertEqual(self.client.get('/api/projects/').data['count'], 1)
        self.assertEqual(self.client.get('/api/time-entries/').data['count'], 1)

    def test_manager_cannot_see_drafts_costs_or_financial_endpoints(self):
        self.entry()
        self.sign_in(self.manager)
        self.assertEqual(self.client.get('/api/time-entries/').data['count'], 0)
        for user in self.client.get('/api/users/').data['results']:
            self.assertNotIn('hourly_cost', user)
            self.assertNotIn('email', user)
        project = self.client.get('/api/projects/').data['results'][0]
        self.assertNotIn('hourly_rate', project)
        self.assertNotIn('budget', project)
        for url in ['/api/invoices/', '/api/payments/']:
            self.assertEqual(self.client.get(url).status_code, 403)

    def test_technician_cannot_access_other_workers_entries_or_escalate_role(self):
        entry = self.entry()
        self.sign_in(self.other_tech)
        self.assertEqual(self.client.get('/api/time-entries/').data['count'], 0)
        self.assertEqual(self.client.patch(f'/api/time-entries/{entry.pk}/', {'description': 'Changed'}).status_code, 404)
        self.assertEqual(self.client.patch(f'/api/users/{self.other_tech.pk}/', {'role': 'ADMIN'}).status_code, 403)
        self.assertEqual(self.client.post('/api/time-entries/', self.payload(), format='json').status_code, 400)

    def test_only_project_manager_can_approve(self):
        entry = self.entry('SUBMITTED')
        for user in [self.admin, self.supervisor, self.tech]:
            self.sign_in(user)
            self.assertEqual(self.client.post(f'/api/time-entries/{entry.pk}/approve/').status_code, 403)

    def test_rejection_requires_reason_and_allows_correction_and_resubmission(self):
        entry = self.entry('SUBMITTED')
        self.sign_in(self.manager)
        url = f'/api/time-entries/{entry.pk}/reject/'
        self.assertEqual(self.client.post(url, {'reason': '   '}).status_code, 400)
        self.assertEqual(self.client.post(url, {'reason': 'Préciser les travaux.'}).status_code, 200)
        self.sign_in(self.tech)
        self.assertEqual(self.client.patch(f'/api/time-entries/{entry.pk}/', {'description': 'Remplacement du moteur'}).status_code, 200)
        self.assertEqual(self.client.post(f'/api/time-entries/{entry.pk}/submit/').status_code, 200)
        entry.refresh_from_db()
        self.assertEqual(entry.rejection_reason, '')
        self.assertTrue(entry.events.filter(comment='Préciser les travaux.').exists())

    def test_submitted_and_approved_entries_cannot_be_edited_or_deleted(self):
        entry = self.entry('SUBMITTED')
        self.sign_in(self.tech)
        self.assertEqual(self.client.patch(f'/api/time-entries/{entry.pk}/', {'description': 'Tampered'}).status_code, 400)
        self.assertEqual(self.client.delete(f'/api/time-entries/{entry.pk}/').status_code, 405)
        entry.status = 'APPROVED'
        entry.save()
        self.assertEqual(self.client.patch(f'/api/time-entries/{entry.pk}/', {'status': 'DRAFT'}).status_code, 400)

    def test_overlaps_invalid_breaks_and_future_times_are_rejected(self):
        self.sign_in(self.tech)
        for values in [self.payload(break_minutes=540), self.payload(end=self.start.isoformat()),
                       self.payload(start=(timezone.now() + timedelta(days=1)).isoformat(),
                                    end=(timezone.now() + timedelta(days=1, hours=2)).isoformat())]:
            self.assertEqual(self.client.post('/api/time-entries/', values, format='json').status_code, 400)
        self.entry()
        self.assertEqual(self.client.post('/api/time-entries/', self.payload(), format='json').status_code, 400)
        self.assertEqual(TimeEntry.objects.count(), 1)

    def test_cannot_forge_approval_or_another_technician_on_create(self):
        self.sign_in(self.tech)
        response = self.client.post('/api/time-entries/', self.payload(status='APPROVED', technician=self.other_tech.pk), format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'DRAFT')
        self.assertEqual(response.data['technician'], self.tech.pk)

    def test_invoice_rejects_unapproved_duplicate_and_cross_project_entries(self):
        entry = self.entry('DRAFT')
        self.sign_in(self.admin)
        payload = {'project': self.project.pk, 'entry_ids': [entry.pk], 'due_date': str(timezone.localdate()), 'tax_percent': 0}
        self.assertEqual(self.client.post('/api/invoices/', payload, format='json').status_code, 400)
        entry.status = 'APPROVED'
        entry.save()
        self.assertEqual(self.client.post('/api/invoices/', {**payload, 'entry_ids': [entry.pk, entry.pk]}, format='json').status_code, 400)
        self.assertEqual(self.client.post('/api/invoices/', {**payload, 'project': self.other_project.pk}, format='json').status_code, 400)
        self.issue(entry)
        self.assertEqual(self.client.post('/api/invoices/', payload, format='json').status_code, 400)
        self.assertEqual(Invoice.objects.count(), 1)

    def test_invoice_snapshot_survives_rate_and_client_changes(self):
        invoice = self.issue(self.entry('APPROVED'))
        self.project.hourly_rate = Decimal('90')
        self.project.save()
        self.company.name = 'Nouveau nom'
        self.company.save()
        response = self.client.get(f"/api/invoices/{invoice['id']}/")
        self.assertEqual(response.data['total'], '432.00')
        self.assertEqual(response.data['lines'][0]['rate'], '45.00')
        self.assertEqual(response.data['client_name'], 'Industrie Alpha')

    def test_overpayments_negative_payments_and_financial_edits_are_blocked(self):
        invoice = self.issue(self.entry('APPROVED'))
        for amount in ['433.00', '-1.00', '0.00']:
            response = self.client.post('/api/payments/', {'invoice': invoice['id'], 'amount': amount,
                                        'date': str(timezone.localdate()), 'method': 'TRANSFER'}, format='json')
            self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(self.client.patch(f"/api/invoices/{invoice['id']}/", {'total': '1.00'}).status_code, 405)

    def test_project_requires_manager_of_same_client(self):
        self.sign_in(self.admin)
        response = self.client.post('/api/projects/', {'name': 'Invalid', 'site': 'A', 'client': self.company.pk,
                                    'project_manager': self.other_manager.pk, 'hourly_rate': '10.00'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_project_accepts_free_text_project_manager_name(self):
        self.sign_in(self.admin)
        response = self.client.post('/api/projects/', {
            'name': 'Free-text manager project', 'site': 'A', 'client': self.company.pk,
            'manager_name': 'External Project Lead', 'hourly_rate': '10.00',
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        project = Project.objects.get(pk=response.data['id'])
        self.assertEqual(project.manager_name, 'External Project Lead')
        self.assertIsNone(project.project_manager_id)
        self.assertEqual(response.data['manager_name'], 'External Project Lead')

    def test_project_labor_cost_uses_fixed_holiday_rate_once_per_technician_day(self):
        self.project.technician_hourly_rate = Decimal('25.00')
        self.project.holiday_day_rate = Decimal('100.00')
        self.project.save(update_fields=['technician_hourly_rate', 'holiday_day_rate'])
        holiday_date = timezone.localtime(self.start).date()
        PublicHoliday.objects.create(name='Jour férié test', date=holiday_date)
        for offset in [0, 2]:
            TimeEntry.objects.create(
                technician=self.tech, project=self.project,
                start=self.start + timedelta(hours=offset),
                end=self.start + timedelta(hours=offset + 1),
                break_minutes=0, description='Travail jour férié', status='APPROVED',
            )
        regular_start = self.start - timedelta(days=1)
        TimeEntry.objects.create(
            technician=self.tech, project=self.project,
            start=regular_start, end=regular_start + timedelta(hours=2),
            break_minutes=0, description='Travail normal', status='APPROVED',
        )

        self.sign_in(self.admin)
        response = self.client.get(f'/api/projects/{self.project.pk}/')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['technician_labor_cost'], Decimal('150.00'))

    def test_technician_earnings_include_only_own_validated_hours(self):
        self.project.technician_hourly_rate = Decimal('25.00')
        self.project.save(update_fields=['technician_hourly_rate'])
        self.entry('APPROVED')
        self.entry('INVOICED')
        for status in ['DRAFT', 'SUBMITTED', 'REJECTED']:
            self.entry(status)
        TimeEntry.objects.create(
            technician=self.other_tech, project=self.project, start=self.start,
            end=self.start + timedelta(hours=8), description='Autre technicien', status='APPROVED',
        )
        # Keep historical earnings visible after an assignment ends.
        self.project.technicians.remove(self.tech)
        self.project.status = 'COMPLETED'
        self.project.save(update_fields=['status'])
        self.sign_in(self.tech)
        response = self.client.get('/api/projects/earnings/')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['count'], 1)
        row = response.data['results'][0]
        self.assertEqual(row['id'], self.project.pk)
        self.assertEqual(row['status'], 'COMPLETED')
        self.assertEqual(row['hours'], '16.00')
        self.assertEqual(row['amount'], '400.00')
        self.assertEqual(row['hourly_rate'], '25.00')
        self.assertEqual(set(row), {'id', 'name', 'client_name', 'site', 'status', 'hours',
                                    'hourly_rate', 'holiday_day_rate', 'amount', 'currency'})
        for path in ['/api/payments/', '/api/invoices/']:
            self.assertEqual(self.client.get(path).status_code, 403)

    def test_technician_earnings_group_projects_and_count_holiday_once(self):
        self.project.technician_hourly_rate = Decimal('25.00')
        self.project.holiday_day_rate = Decimal('100.00')
        self.project.save(update_fields=['technician_hourly_rate', 'holiday_day_rate'])
        PublicHoliday.objects.create(name='Jour férié', date=timezone.localtime(self.start).date())
        for offset in [0, 2]:
            TimeEntry.objects.create(
                technician=self.tech, project=self.project, start=self.start + timedelta(hours=offset),
                end=self.start + timedelta(hours=offset + 1), description='Férié', status='APPROVED',
            )
        regular_start = self.start - timedelta(days=1)
        TimeEntry.objects.create(
            technician=self.tech, project=self.project, start=regular_start,
            end=regular_start + timedelta(hours=2), description='Normal', status='INVOICED',
        )
        self.other_project.technicians.add(self.tech)
        self.sign_in(self.tech)
        response = self.client.get('/api/projects/earnings/')
        self.assertEqual(response.status_code, 200, response.data)
        rows = {row['id']: row for row in response.data['results']}
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[self.project.pk]['hours'], '4.00')
        self.assertEqual(rows[self.project.pk]['amount'], '150.00')
        self.assertEqual(rows[self.other_project.pk]['hours'], '0.00')
        self.assertEqual(rows[self.other_project.pk]['amount'], '0.00')

    def test_technician_earnings_are_read_only_and_require_technician(self):
        self.assertIn(self.client.get('/api/projects/earnings/').status_code, [401, 403])
        for user in [self.admin, self.supervisor, self.manager]:
            self.sign_in(user)
            self.assertEqual(self.client.get('/api/projects/earnings/').status_code, 403)
        self.sign_in(self.tech)
        self.assertEqual(self.client.post('/api/projects/earnings/', {}).status_code, 405)

    def test_invoice_uses_fixed_holiday_billing_rate_once_per_technician_day(self):
        holiday_date = timezone.localtime(self.start).date()
        PublicHoliday.objects.create(name='Jour férié facturé', date=holiday_date)
        self.project.holiday_billing_day_rate = Decimal('250.00')
        self.project.save(update_fields=['holiday_billing_day_rate'])
        entries = [
            TimeEntry.objects.create(
                technician=self.tech, project=self.project,
                start=self.start + timedelta(hours=offset),
                end=self.start + timedelta(hours=offset + 2),
                break_minutes=0, description='Travail jour férié', status='APPROVED',
            )
            for offset in [0, 3]
        ]
        self.sign_in(self.admin)
        response = self.client.post('/api/invoices/', {
            'project': self.project.pk, 'entry_ids': [entry.pk for entry in entries],
            'due_date': str(timezone.localdate() + timedelta(days=30)), 'tax_percent': '0',
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['subtotal'], '250.00')
        self.assertEqual(sum(Decimal(line['amount']) for line in response.data['lines']), Decimal('250.00'))

    def test_admin_can_manage_public_holiday_dates(self):
        self.sign_in(self.admin)
        response = self.client.post('/api/holidays/', {'name': 'Fête test', 'date': '2026-01-01'}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertTrue(PublicHoliday.objects.filter(name='Fête test', date='2026-01-01').exists())
        duplicate = self.client.post('/api/holidays/', {'name': 'Autre', 'date': '2026-01-01'}, format='json')
        self.assertEqual(duplicate.status_code, 400)
        deletion = self.client.delete(f"/api/holidays/{response.data['id']}/")
        self.assertEqual(deletion.status_code, 204)

    def test_client_registration_fields_are_created_and_updated(self):
        self.sign_in(self.admin)
        payload = {
            'name': 'Nouvelle société', 'rc': 'RC-123', 'nif': 'NIF-456',
            'article_number': 'ART-789', 'nis': 'NIS-012', 'billing_address': 'Adresse client',
            'start_work_date': '2020-05-14', 'is_active': False,
        }
        response = self.client.post('/api/clients/', payload, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        for field in ['rc', 'nif', 'article_number', 'nis', 'billing_address', 'start_work_date']:
            self.assertEqual(response.data[field], payload[field])
        self.assertFalse(response.data['is_active'])
        url = f"/api/clients/{response.data['id']}/"
        response = self.client.patch(url, {'nif': 'NIF-NEW', 'is_active': True}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['nif'], 'NIF-NEW')
        self.assertTrue(response.data['is_active'])

    def test_client_logo_upload_and_download(self):
        self.sign_in(self.admin)
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        with override_settings(MEDIA_ROOT=folder.name):
            pixmap = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 120, 80), False)
            pixmap.clear_with(0x336699)
            response = self.client.post('/api/clients/', {
                'name': 'Logo Test',
                'logo': SimpleUploadedFile('company.png', pixmap.tobytes('png'), content_type='image/png'),
            }, format='multipart')
            self.assertEqual(response.status_code, 201, response.data)
            self.assertEqual(response.data['logo_url'], f"/api/clients/{response.data['id']}/logo/")
            download = self.client.get(response.data['logo_url'])
            self.assertEqual(download.status_code, 200)
            self.assertEqual(download['Content-Type'], 'image/png')
            self.assertTrue(b''.join(download.streaming_content).startswith(b'\x89PNG\r\n\x1a\n'))

    def test_client_delete_is_admin_only_and_refuses_clients_with_history(self):
        self.sign_in(self.admin)
        unused = Client.objects.create(name='Unused client')
        self.assertEqual(self.client.delete(f'/api/clients/{unused.pk}/').status_code, 204)
        unused.refresh_from_db()
        self.assertIsNotNone(unused.deleted_at)
        response = self.client.delete(f'/api/clients/{self.company.pk}/')
        self.assertEqual(response.status_code, 204)
        self.company.refresh_from_db()
        self.assertIsNotNone(self.company.deleted_at)

        another = Client.objects.create(name='Supervisor cannot delete')
        self.sign_in(self.supervisor)
        self.assertEqual(self.client.delete(f'/api/clients/{another.pk}/').status_code, 403)
        self.assertTrue(Client.objects.filter(pk=another.pk).exists())

    def test_user_creation_hashes_password_and_requires_client_for_manager(self):
        self.sign_in(self.admin)
        payload = {'username': 'new-manager', 'role': 'PROJECT_MANAGER', 'password': 'Secure-Password-839!'}
        self.assertEqual(self.client.post('/api/users/', payload, format='json').status_code, 400)
        response = self.client.post('/api/users/', {**payload, 'client': self.company.pk}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertNotIn('password', response.data)
        self.assertTrue(User.objects.get(pk=response.data['id']).check_password(payload['password']))

    def test_user_with_project_cannot_change_client_and_admin_cannot_disable_self(self):
        self.sign_in(self.admin)
        self.assertEqual(self.client.patch(f'/api/users/{self.manager.pk}/', {'client': self.other_company.pk}).status_code, 400)
        self.assertEqual(self.client.patch(f'/api/users/{self.admin.pk}/', {'is_active': False}, format='json').status_code, 400)

    def test_anonymous_requests_are_rejected(self):
        for endpoint in ['projects', 'users', 'clients', 'time-entries', 'invoices', 'payments', 'dashboard']:
            self.assertEqual(self.client.get(f'/api/{endpoint}/').status_code, 403)

    def test_session_login_requires_csrf_and_logout_invalidates_session(self):
        client = APIClient(enforce_csrf_checks=True)
        payload = {'username': 'admin', 'password': 'Test-Strong-839!'}
        self.assertEqual(client.post('/api/auth/login/', payload).status_code, 403)
        token = client.get('/api/auth/session/').data['csrfToken']
        response = client.post('/api/auth/login/', payload, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['user']['role'], 'ADMIN')
        token = response.data['csrfToken']
        self.assertEqual(client.post('/api/auth/logout/', HTTP_X_CSRFTOKEN=token).status_code, 200)
        self.assertIsNone(client.get('/api/auth/session/').data['user'])

    def test_superuser_created_with_admin_role(self):
        user = User.objects.create_superuser('owner', password='Owner-Password-123!')
        self.assertEqual(user.role, 'ADMIN')
        self.assertTrue(user.is_staff)
