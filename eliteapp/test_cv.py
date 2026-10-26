import calendar
import base64
from datetime import timedelta
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
import pymupdf
from rest_framework.test import APITestCase

from .cv import experience_section
from .models import User


def pdf_upload(text=None):
    with pymupdf.open() as document:
        page = document.new_page()
        if text:
            page.insert_text((60, 70), text)
        return SimpleUploadedFile('cv.pdf', document.tobytes(), content_type='application/pdf')


class TechnicianProfileTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user('cv-admin', role='ADMIN')
        cls.supervisor = User.objects.create_user('cv-supervisor', role='SUPERVISOR')
        cls.tech = User.objects.create_user('cv-technician', role='TECHNICIAN')

    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        settings = override_settings(MEDIA_ROOT=folder.name)
        settings.enable()
        self.addCleanup(settings.disable)
        self.client.force_authenticate(self.admin)

    def test_profile_and_cv_create_update_and_download(self):
        response = self.client.post('/api/users/', {
            'username': 'new-technician', 'password': 'B7!rN4@zQ9$vLm2',
            'first_name': 'Amine', 'last_name': 'Test', 'role': 'TECHNICIAN', 'client': '',
            'birth_date': '1994-03-12', 'address': '12 rue des Ateliers',
            'phone': '0555123456', 'email': 'amine@example.com', 'specialty': 'Soudeur',
            'experience': 'Maintenance industrielle depuis 2020.', 'certificates': 'Habilitation électrique B1V',
            'cv': pdf_upload('CV test'), 'is_active': 'true',
        }, format='multipart')
        self.assertEqual(response.status_code, 201, response.data)
        identifier = response.data['id']
        url = f'/api/users/{identifier}/'
        saved = self.client.get(url).data
        self.assertEqual(saved['birth_date'], '1994-03-12')
        self.assertEqual(saved['experience'], 'Maintenance industrielle depuis 2020.')
        self.assertEqual(saved['certificates'], 'Habilitation électrique B1V')
        self.assertEqual(saved['address'], '12 rue des Ateliers')
        self.assertEqual(saved['phone'], '0555123456')
        self.assertEqual(saved['email'], 'amine@example.com')
        self.assertEqual(saved['specialty'], 'Soudeur')
        self.assertNotIn('cv', saved)
        self.assertEqual(self.client.patch(url, {'experience': 'Expérience corrigée.'}, format='json').status_code, 200)
        self.assertEqual(self.client.get(url).data['cv_url'], saved['cv_url'])
        for role in [self.admin, self.supervisor]:
            self.client.force_authenticate(role)
            download = self.client.get(saved['cv_url'])
            self.assertEqual(download.status_code, 200)
            self.assertTrue(b''.join(download.streaming_content).startswith(b'%PDF-'))
            self.assertIn('attachment', download['Content-Disposition'])
        self.client.force_authenticate(self.tech)
        self.assertEqual(self.client.get(saved['cv_url']).status_code, 403)
        personal = self.client.get(f'/api/users/{self.tech.pk}/').data
        for field in ['birth_date', 'address', 'experience', 'certificates', 'cv_url', 'cv_name']:
            self.assertNotIn(field, personal)
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get(saved['cv_url']).status_code, 403)

    def test_technician_matricules_are_generated_sequentially_and_read_only(self):
        first = self.client.post('/api/users/', {
            'username': 'numbered-tech-one', 'password': 'B7!rN4@zQ9$vLm2',
            'role': 'TECHNICIAN', 'client': '',
        }, format='json')
        second = self.client.post('/api/users/', {
            'username': 'numbered-tech-two', 'password': 'B7!rN4@zQ9$vLm2',
            'role': 'TECHNICIAN', 'client': '',
        }, format='json')
        self.assertEqual(first.status_code, 201, first.data)
        self.assertEqual(second.status_code, 201, second.data)
        year = timezone.localdate().year
        self.assertRegex(first.data['employee_number'], rf'^CP-{year}-\d{{5}}$')
        self.assertEqual(
            int(second.data['employee_number'].rsplit('-', 1)[1]),
            int(first.data['employee_number'].rsplit('-', 1)[1]) + 1,
        )
        response = self.client.patch(f"/api/users/{first.data['id']}/", {
            'employee_number': 'CUSTOM',
        }, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['employee_number'], first.data['employee_number'])

    def test_blank_birth_date_with_multipart_cv_and_future_date(self):
        url = f'/api/users/{self.tech.pk}/'
        response = self.client.patch(url, {'birth_date': '', 'client': '', 'cv': pdf_upload('Test')}, format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertIsNone(response.data['birth_date'])
        response = self.client.patch(url, {'birth_date': str(timezone.localdate() + timedelta(days=1))}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('birth_date', response.data)
        today = timezone.localdate()
        cutoff_day = min(today.day, calendar.monthrange(today.year - 18, today.month)[1])
        adult_date = today.replace(year=today.year - 18, day=cutoff_day)
        underage_date = adult_date + timedelta(days=1)
        response = self.client.patch(url, {'birth_date': str(underage_date)}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('18 ans', str(response.data['birth_date']))
        response = self.client.patch(url, {'birth_date': str(adult_date)}, format='json')
        self.assertEqual(response.status_code, 200, response.data)

    def test_phone_number_requires_exactly_ten_digits(self):
        url = f'/api/users/{self.tech.pk}/'
        for phone in ['123456789', '12345678901', '12345 6789', '12345678a0']:
            response = self.client.patch(url, {'phone': phone}, format='json')
            self.assertEqual(response.status_code, 400, response.data)
            self.assertIn('phone', response.data)
        response = self.client.patch(url, {'phone': '0123456789'}, format='json')
        self.assertEqual(response.status_code, 200, response.data)

    def test_technician_profile_text_fields_are_saved_in_uppercase(self):
        url = f'/api/users/{self.tech.pk}/'
        response = self.client.patch(url, {
            'last_name': 'arouche', 'first_name': 'mohamed',
            'specialty': 'mechanical tech', 'address': 'rue des ateliers',
        }, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['last_name'], 'AROUCHE')
        self.assertEqual(response.data['first_name'], 'MOHAMED')
        self.assertEqual(response.data['specialty'], 'MECHANICAL TECH')
        self.assertEqual(response.data['address'], 'RUE DES ATELIERS')
        response = self.client.get(url)
        self.assertEqual(response.data['last_name'], 'AROUCHE')
        self.assertEqual(response.data['first_name'], 'MOHAMED')
        self.assertEqual(response.data['specialty'], 'MECHANICAL TECH')
        self.assertEqual(response.data['address'], 'RUE DES ATELIERS')

    def test_invalid_files_are_rejected_on_save_and_extraction(self):
        for name, contents in [('cv.pdf', b'fake pdf'), ('cv.svg', b'<svg/>'), ('cv.png', b'fake image')]:
            for url in [f'/api/users/{self.tech.pk}/', '/api/users/extract-cv/']:
                method = self.client.patch if '/extract-cv/' not in url else self.client.post
                response = method(url, {'cv': SimpleUploadedFile(name, contents)}, format='multipart')
                self.assertEqual(response.status_code, 400, response.data)
        upload = SimpleUploadedFile('cv.pdf', b'%PDF-' + b'x' * (10 * 1024 * 1024))
        response = self.client.post('/api/users/extract-cv/', {'cv': upload}, format='multipart')
        self.assertEqual(response.status_code, 400)

    def test_pdf_experience_extraction_does_not_save_or_include_education(self):
        response = self.client.post('/api/users/extract-cv/', {'cv': pdf_upload(
            'Amine Test\nEXPERIENCE PROFESSIONNELLE\n2020 - 2025 : Maintenance industrielle\nFORMATION\nBTS'
        )}, format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertIn('Maintenance industrielle', response.data['experience'])
        self.assertNotIn('BTS', response.data['experience'])
        self.tech.refresh_from_db()
        self.assertFalse(self.tech.cv)
        self.assertEqual(self.tech.experience, '')

    def test_saved_cv_can_be_extracted_from_edit_form(self):
        self.tech.cv.save('saved-cv.pdf', pdf_upload(
            'EXPERIENCE PROFESSIONNELLE\nMaintenance industrielle depuis 2020.'
        ), save=True)
        response = self.client.post(f'/api/users/{self.tech.pk}/extract-cv/')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertIn('Maintenance industrielle', response.data['experience'])
        self.tech.refresh_from_db()
        self.assertTrue(self.tech.cv)
        self.assertEqual(self.tech.experience, '')

    def test_formatted_experience_is_preserved_on_save_and_reload(self):
        experience = ('<!--copetrolite-experience:v1--><p><b>Technicien</b> '
                      '<u>2020–2026</u></p><ul><li>Maintenance industrielle</li></ul>')
        url = f'/api/users/{self.tech.pk}/'
        response = self.client.patch(url, {'experience': experience}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(self.client.get(url).data['experience'], experience)
        response = self.client.patch(url, {'experience': 'x' * 20001}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.get(url).data['experience'], experience)

    def test_two_column_cv_keeps_jobs_and_dates_across_pages(self):
        with pymupdf.open() as document:
            page = document.new_page()
            page.insert_text((50, 60), 'EDUCATION')
            page.insert_text((50, 100), 'University degree')
            page.insert_text((250, 60), 'EXPERIENCE')
            page.insert_text((250, 100), 'Research Professional')
            page.insert_text((500, 100), '2022')
            page.insert_text((250, 130), 'Develop technical skills in GIS.')
            page.insert_text((50, 160), 'SKILLS')
            page.insert_text((50, 190), 'Sidebar content')
            page.insert_text((250, 190), 'Urban Planner')
            page = document.new_page()
            page.insert_text((60, 60), 'Urban Planning Inspector')
            page.insert_text((500, 60), '2020')
            page.insert_text((60, 100), 'Architect at Example Company')
            page.insert_text((60, 160), 'TECHNICAL SKILLS')
            page.insert_text((60, 190), 'Software list')
            upload = SimpleUploadedFile('columns.pdf', document.tobytes(), content_type='application/pdf')
        self.tech.cv.save('columns.pdf', upload, save=True)
        response = self.client.post(f'/api/users/{self.tech.pk}/extract-cv/')
        self.assertEqual(response.status_code, 200, response.data)
        experience = response.data['experience']
        for expected in ['Research Professional', '2022', 'Develop technical skills in GIS.',
                         'Urban Planner', 'Urban Planning Inspector', '2020', 'Architect at Example Company']:
            self.assertIn(expected, experience)
        for excluded in ['University degree', 'Sidebar content', 'TECHNICAL SKILLS', 'Software list']:
            self.assertNotIn(excluded, experience)
        response = self.client.patch(f'/api/users/{self.tech.pk}/', {'experience': experience}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(self.client.get(f'/api/users/{self.tech.pk}/').data['experience'], experience)

    def test_pdf_experience_in_left_column_excludes_right_sidebar(self):
        with pymupdf.open() as document:
            page = document.new_page()
            page.insert_text((50, 60), 'EXPERIENCE')
            page.insert_text((50, 100), 'Maintenance technician')
            page.insert_text((400, 60), 'EDUCATION')
            page.insert_text((400, 100), 'University degree')
            page.insert_text((50, 160), 'CERTIFICATS')
            page.insert_text((50, 190), 'Certificate details')
            upload = SimpleUploadedFile('columns.pdf', document.tobytes(), content_type='application/pdf')
        response = self.client.post('/api/users/extract-cv/', {'cv': upload}, format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['experience'], 'Maintenance technician')

    def test_cv_image_is_automatically_saved_as_profile_photo(self):
        photo = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 160, 200), False)
        photo.clear_with(0x336699)
        with pymupdf.open() as document:
            page = document.new_page()
            page.insert_image(page.rect, stream=photo.tobytes('png'))
            cv = SimpleUploadedFile('photo-cv.pdf', document.tobytes(), content_type='application/pdf')
        response = self.client.post('/api/users/', {
            'username': 'photo-from-cv', 'password': 'B7!rN4@zQ9$vLm2',
            'role': 'TECHNICIAN', 'client': '', 'cv': cv,
        }, format='multipart')
        self.assertEqual(response.status_code, 201, response.data)
        cv_url = response.data['cv_url']
        self.assertTrue(cv_url)
        saved_user = User.objects.get(pk=response.data['id'])
        self.assertTrue(saved_user.cv)
        self.assertTrue(response.data['photo_url'])
        response = self.client.get(response.data['photo_url'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertTrue(b''.join(response.streaming_content).startswith(b'\x89PNG\r\n\x1a\n'))
        cv_download = self.client.get(cv_url)
        self.assertEqual(cv_download.status_code, 200)
        self.assertTrue(b''.join(cv_download.streaming_content).startswith(b'%PDF-'))

    def test_photo_can_be_extracted_from_cv_before_saving(self):
        photo = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 160, 200), False)
        photo.clear_with(0x336699)
        with pymupdf.open() as document:
            page = document.new_page()
            page.insert_image(page.rect, stream=photo.tobytes('png'))
            cv = SimpleUploadedFile('photo-cv.pdf', document.tobytes(), content_type='application/pdf')
        response = self.client.post('/api/users/extract-cv-photo/', {'cv': cv}, format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertTrue(base64.b64decode(response.data['photo']).startswith(b'\x89PNG\r\n\x1a\n'))
        self.tech.refresh_from_db()
        self.assertFalse(self.tech.photo)

    def test_saved_cv_fills_missing_profile_photo_and_photo_upload_is_validated(self):
        photo = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 160, 200), False)
        photo.clear_with(0x336699)
        with pymupdf.open() as document:
            page = document.new_page()
            page.insert_image(page.rect, stream=photo.tobytes('png'))
            self.tech.cv.save('photo-cv.pdf', SimpleUploadedFile('photo-cv.pdf', document.tobytes()), save=True)
        response = self.client.patch(f'/api/users/{self.tech.pk}/', {'phone': '12345'}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertTrue(response.data['photo_url'])

        response = self.client.patch(f'/api/users/{self.tech.pk}/', {
            'photo': SimpleUploadedFile('invalid.png', b'not an image'),
        }, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.tech.refresh_from_db()
        self.assertTrue(self.tech.photo)

    def test_explicit_profile_photo_takes_priority_over_cv_image(self):
        cv_photo = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 160, 200), False)
        cv_photo.clear_with(0x336699)
        with pymupdf.open() as document:
            page = document.new_page()
            page.insert_image(page.rect, stream=cv_photo.tobytes('png'))
            cv = SimpleUploadedFile('photo-cv.pdf', document.tobytes(), content_type='application/pdf')
        chosen_photo = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 120, 120), False)
        chosen_photo.clear_with(0x993366)
        response = self.client.post('/api/users/', {
            'username': 'chosen-photo', 'password': 'B7!rN4@zQ9$vLm2',
            'role': 'TECHNICIAN', 'client': '', 'cv': cv,
            'photo': SimpleUploadedFile('chosen.png', chosen_photo.tobytes('png'), content_type='image/png'),
        }, format='multipart')
        self.assertEqual(response.status_code, 201, response.data)
        download = self.client.get(response.data['photo_url'])
        self.assertEqual(download.status_code, 200)
        self.assertTrue(b''.join(download.streaming_content).startswith(b'\x89PNG\r\n\x1a\n'))
        self.assertTrue(response.data['photo_url'])

    def test_missing_section_provides_text_for_manual_review(self):
        response = self.client.post('/api/users/extract-cv/', {'cv': pdf_upload(
            'Technicien de maintenance depuis 2020, entretien des installations industrielles.'
        )}, format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['experience'], '')
        self.assertTrue(response.data['warning'])
        self.assertIn('Technicien', response.data['extracted_text'])

    @patch('eliteapp.cv.ocr_image', return_value='EXPERIENCE\nMaintenance 2020-2025\nCERTIFICATS\nB1V')
    def test_image_and_scanned_pdf_use_ocr(self, ocr):
        with pymupdf.open() as document:
            page = document.new_page()
            page.insert_text((60, 70), 'CV test')
            image = page.get_pixmap().tobytes('png')
        for upload in [SimpleUploadedFile('cv.png', image, content_type='image/png'), pdf_upload()]:
            response = self.client.post('/api/users/extract-cv/', {'cv': upload}, format='multipart')
            self.assertEqual(response.status_code, 200, response.data)
            self.assertEqual(response.data['experience'], 'Maintenance 2020-2025')
        self.assertEqual(ocr.call_count, 2)

    def test_extraction_restricted_to_admins(self):
        for role in [self.supervisor, self.tech, None]:
            self.client.force_authenticate(role)
            response = self.client.post('/api/users/extract-cv/', {'cv': pdf_upload('test')}, format='multipart')
            self.assertEqual(response.status_code, 403)
            response = self.client.post(f'/api/users/{self.tech.pk}/extract-cv/')
            self.assertEqual(response.status_code, 403)

    def test_french_and_english_section_headings(self):
        self.assertEqual(experience_section('Expériences professionnelles :\nSoudeur\nCompétences\nSoudure'), 'Soudeur')
        self.assertEqual(experience_section('Work experience\nWelder\nEducation\nDiploma'), 'Welder')

    def test_multiple_certificates_on_create_and_individual_changes(self):
        response = self.client.post('/api/users/', {
            'username': 'certificates-user', 'password': 'B7!rN4@zQ9$vLm2',
            'role': 'TECHNICIAN', 'client': '', 'birth_date': '',
            'certificate_files': [pdf_upload('First certificate'), pdf_upload('Second certificate')],
            'cv': pdf_upload('CV'),
        }, format='multipart')
        self.assertEqual(response.status_code, 201, response.data)
        url = f"/api/users/{response.data['id']}/"
        documents = response.data['certificate_documents']
        self.assertEqual(len(documents), 2)
        self.assertEqual([doc['name'] for doc in documents], ['cv.pdf', 'cv.pdf'])
        user = User.objects.get(pk=response.data['id'])
        first = user.certificate_documents.get(pk=documents[0]['id'])
        self.assertTrue(first.file.storage.exists(first.file.name))
        download = self.client.get(documents[0]['url'])
        self.assertEqual(download.status_code, 200)
        self.assertTrue(b''.join(download.streaming_content).startswith(b'%PDF-'))
        # Editing another field preserves all attachments.
        response = self.client.patch(url, {'phone': '123'}, format='json')
        self.assertEqual(len(response.data['certificate_documents']), 2)
        # One multipart request can remove one certificate and add another, preserving the CV.
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.patch(url, {
                'remove_certificate_ids': [documents[0]['id']],
                'certificate_files': [pdf_upload('Replacement certificate')],
            }, format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(len(response.data['certificate_documents']), 2)
        self.assertIn(documents[1]['id'], [doc['id'] for doc in response.data['certificate_documents']])
        self.assertNotIn(documents[0]['id'], [doc['id'] for doc in response.data['certificate_documents']])
        self.assertFalse(first.file.storage.exists(first.file.name))
        self.assertTrue(response.data['cv_url'])
        self.assertEqual(self.client.get(documents[0]['url']).status_code, 404)
        ids = [doc['id'] for doc in response.data['certificate_documents']]
        response = self.client.patch(url, {'remove_certificate_ids': ids}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['certificate_documents'], [])

    def test_certificate_permissions_and_ownership(self):
        url = f'/api/users/{self.tech.pk}/'
        response = self.client.patch(url, {'certificate_files': [pdf_upload('Certificate')]}, format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        doc = response.data['certificate_documents'][0]
        wrong_url = f'/api/users/{self.admin.pk}/certificates/{doc["id"]}/'
        self.assertEqual(self.client.get(wrong_url).status_code, 404)
        response = self.client.patch(f'/api/users/{self.admin.pk}/', {'remove_certificate_ids': [doc['id']]}, format='json')
        self.assertEqual(response.status_code, 400)
        self.client.force_authenticate(self.supervisor)
        response = self.client.get(doc['url'])
        self.assertEqual(response.status_code, 200)
        # Consume Django's test-client stream so it closes without ending the test transaction.
        self.assertTrue(b''.join(response.streaming_content).startswith(b'%PDF-'))
        self.assertEqual(self.client.patch(url, {'certificate_files': [pdf_upload('Forbidden')]}, format='multipart').status_code, 403)
        for role in [self.tech, None]:
            self.client.force_authenticate(role)
            self.assertEqual(self.client.get(doc['url']).status_code, 403)
        self.client.force_authenticate(self.tech)
        self.assertNotIn('certificate_documents', self.client.get(url).data)

    def test_cv_and_certificate_previews_preserve_downloads_and_permissions(self):
        response = self.client.patch(f'/api/users/{self.tech.pk}/', {
            'cv': pdf_upload('CV preview'),
            'certificate_files': [pdf_upload('Certificate preview')],
        }, format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        urls = [response.data['cv_url'], response.data['certificate_documents'][0]['url']]
        for role in [self.admin, self.supervisor]:
            self.client.force_authenticate(role)
            for url in urls:
                for suffix, disposition in [('', 'attachment'), ('?preview=1', 'inline')]:
                    document = self.client.get(url + suffix)
                    self.assertEqual(document.status_code, 200)
                    self.assertTrue(document['Content-Disposition'].startswith(disposition))
                    self.assertEqual(document['Content-Type'], 'application/pdf')
                    self.assertEqual(document['Cache-Control'], 'private, no-store')
                    self.assertEqual(document['X-Content-Type-Options'], 'nosniff')
                    self.assertTrue(b''.join(document.streaming_content).startswith(b'%PDF-'))
        for role in [self.tech, None]:
            self.client.force_authenticate(role)
            for url in urls:
                self.assertEqual(self.client.get(url + '?preview=1').status_code, 403)

    def test_image_previews_have_inline_image_content_type(self):
        with pymupdf.open() as document:
            page = document.new_page(width=100, height=100)
            image = page.get_pixmap().tobytes('png')
        response = self.client.patch(f'/api/users/{self.tech.pk}/', {
            'cv': SimpleUploadedFile('cv.png', image, content_type='image/png'),
            'certificate_files': [SimpleUploadedFile('certificate.png', image, content_type='image/png')],
        }, format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        for url in [response.data['cv_url'], response.data['certificate_documents'][0]['url']]:
            preview = self.client.get(url + '?preview=1')
            self.assertEqual(preview.status_code, 200)
            self.assertEqual(preview['Content-Type'], 'image/png')
            self.assertTrue(preview['Content-Disposition'].startswith('inline'))
            self.assertEqual(b''.join(preview.streaming_content), image)

    def test_invalid_certificate_rejects_entire_batch(self):
        url = f'/api/users/{self.tech.pk}/'
        response = self.client.patch(url, {
            'phone': 'should-not-be-saved',
            'certificate_files': [pdf_upload('Valid'), SimpleUploadedFile('bad.pdf', b'not a PDF')],
        }, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.tech.refresh_from_db()
        self.assertEqual(self.tech.phone, '')
        self.assertEqual(self.tech.certificate_documents.count(), 0)

    def test_image_certificate_upload(self):
        with pymupdf.open() as document:
            page = document.new_page()
            page.insert_text((60, 70), 'Certificate')
            upload = SimpleUploadedFile('habilitation.png', page.get_pixmap().tobytes('png'), content_type='image/png')
        response = self.client.patch(f'/api/users/{self.tech.pk}/', {'certificate_files': [upload]}, format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['certificate_documents'][0]['name'], 'habilitation.png')

    def test_long_documents_and_empty_optional_cv_do_not_block_saving(self):
        with pymupdf.open() as document:
            for index in range(25):
                document.new_page().insert_text((60, 70), f'Certificate page {index + 1}')
            content = document.tobytes()
        response = self.client.post('/api/users/', {
            'username': 'long-documents-user', 'password': 'B7!rN4@zQ9$vLm2',
            'role': 'TECHNICIAN', 'client': '',
            'cv': SimpleUploadedFile('empty.pdf', b'', content_type='application/pdf'),
            'certificate_files': [SimpleUploadedFile('certificate.pdf', content, content_type='application/pdf')],
        }, format='multipart')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['cv_url'], '')
        self.assertEqual(len(response.data['certificate_documents']), 1)
        url = f"/api/users/{response.data['id']}/"
        response = self.client.patch(url, {
            'cv': SimpleUploadedFile('long-cv.pdf', content, content_type='application/pdf'),
        }, format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        cv_name = response.data['cv_name']
        self.assertTrue(cv_name)
        response = self.client.patch(url, {
            'phone': '0123456789',
            'cv': SimpleUploadedFile('empty.pdf', b'', content_type='application/pdf'),
        }, format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['cv_name'], cv_name)
        self.assertEqual(response.data['phone'], '0123456789')
        self.assertEqual(len(response.data['certificate_documents']), 1)
