"""Run the unchanged application API on an isolated demonstration database."""
from pathlib import Path
import sys
import json
import secrets
from datetime import datetime, timedelta, date
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
STATE = ROOT / '.runtime' / 'presentation-demo'
STATE.mkdir(exist_ok=True)
from django.conf import settings
settings.configure(
    BASE_DIR=ROOT, DEBUG=True, SECRET_KEY=secrets.token_urlsafe(40),
    ALLOWED_HOSTS=['127.0.0.1', 'localhost'],
    CSRF_TRUSTED_ORIGINS=['http://127.0.0.1:5179'],
    INSTALLED_APPS=['django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
                    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
                    'rest_framework', 'eliteapp'],
    MIDDLEWARE=['django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware', 'django.contrib.messages.middleware.MessageMiddleware'],
    TEMPLATES=[{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'APP_DIRS': True,
                'OPTIONS': {'context_processors': ['django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages']}}],
    ROOT_URLCONF='coproject.urls', AUTH_USER_MODEL='eliteapp.User',
    DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': STATE/'demo.sqlite3'}},
    DEFAULT_AUTO_FIELD='django.db.models.BigAutoField', USE_TZ=True, TIME_ZONE='Africa/Algiers',
    LANGUAGE_CODE='fr-fr', STATIC_URL='/static/', MEDIA_ROOT=STATE/'uploads',
    APP_CURRENCY='DZD', PASSWORD_HASHERS=['django.contrib.auth.hashers.PBKDF2PasswordHasher'],
    REST_FRAMEWORK={
        'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],
        'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
        'DEFAULT_THROTTLE_RATES': {'anon': '1000/min', 'login': '100/min'},
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 100, 'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer']},
)
import django
django.setup()
from django.core.management import call_command
from django.core.files.base import ContentFile
from django.utils import timezone
from eliteapp.models import User, Client, Project, TimeEntry, TechnicianCertificate
from eliteapp.services import transition_entry, create_invoice, record_payment
import pymupdf

call_command('migrate', verbosity=0)
access_path = STATE/'access.json'
if not User.objects.exists():
    password = secrets.token_urlsafe(24)
    roles = [('demo-admin','ADMIN','Nadia','ADMINISTRATION'), ('demo-superviseur','SUPERVISOR','Karim','COORDINATION'),
             ('demo-tech','TECHNICIAN','AMINE','DEMONSTRATION'), ('demo-tech2','TECHNICIAN','LINA','DEMONSTRATION')]
    people = {}
    for name, role, first, last in roles:
        people[name] = User.objects.create_user(name, password=password, role=role, first_name=first, last_name=last,
            email=name+'@example.invalid', phone='0500000000', specialty='MAINTENANCE INDUSTRIELLE' if role=='TECHNICIAN' else '')
    client = Client.objects.create(name='Atlas Industrie — Démo', contact_name='Responsable exploitation',
        email='contact@example.invalid', phone='0200000000', rc='DEMO-RC-2026', nif='DEMO-NIF', nis='DEMO-NIS',
        article_number='DEMO-001', billing_address='Zone industrielle — Site de démonstration', start_work_date=date(2026,9,1))
    client2 = Client.objects.create(name='Horizon Énergie — Démo', contact_name='Service technique',
        email='horizon@example.invalid', phone='0210000000', billing_address='Site de démonstration Est')
    manager = User.objects.create_user('demo-client', password=password, role='PROJECT_MANAGER', client=client,
        first_name='Samir', last_name='CLIENT DÉMO')
    admin, tech, tech2 = people['demo-admin'], people['demo-tech'], people['demo-tech2']
    p = Project.objects.create(name='Maintenance préventive — Unité A', client=client, site='Atelier mécanique',
        manager_name='Samir — Client démo', access_user=manager, hourly_rate=2500, technician_hourly_rate=1000,
        holiday_billing_day_rate=20000, holiday_day_rate=8000, purchase_order='BC-DEMO-2026-014',
        description='Inspection, maintenance des équipements et compte rendu des interventions.')
    p.technicians.set([tech, tech2])
    p2 = Project.objects.create(name='Inspection équipements — Site Est', client=client2, site='Site Est',
        manager_name='Responsable site Est', hourly_rate=3000, technician_hourly_rate=1200,
        holiday_billing_day_rate=24000, holiday_day_rate=9600)
    p2.technicians.set([tech2])
    # A geometric avatar is explicitly illustrative; no real person or private CV is used.
    avatar = pymupdf.open()
    av = avatar.new_page(width=180, height=220)
    av.draw_rect(av.rect, color=None, fill=(0.88,0.95,0.93))
    av.draw_circle((90,75), 33, color=None, fill=(0.05,0.31,0.34))
    av.draw_oval(pymupdf.Rect(30,115,150,235), color=None, fill=(0.05,0.31,0.34))
    image = av.get_pixmap().tobytes('png')
    cv = pymupdf.open()
    pg = cv.new_page()
    pg.insert_image(pymupdf.Rect(430,35,535,165), stream=image)
    pg.insert_text((50,55), 'AMINE DEMONSTRATION', fontsize=20)
    pg.insert_text((50,88), 'Technicien de maintenance industrielle', fontsize=13)
    pg.insert_text((50,115), 'Document fictif - portrait illustratif', fontsize=10)
    pg.insert_text((50,200), 'EXPERIENCE PROFESSIONNELLE', fontsize=16)
    pg.insert_text((50,235), '2023 - 2026 | Technicien de maintenance industrielle', fontsize=12)
    pg.insert_text((50,258), 'Maintenance preventive des pompes et equipements mecaniques.', fontsize=11)
    pg.insert_text((50,280), 'Diagnostic des anomalies, controles et rapports intervention.', fontsize=11)
    pg.insert_text((50,320), '2020 - 2023 | Technicien atelier', fontsize=12)
    pg.insert_text((50,343), 'Montage, inspection et remise en etat des equipements.', fontsize=11)
    pg.insert_text((50,395), 'FORMATION', fontsize=16)
    pg.insert_text((50,425), 'Diplome technique - maintenance industrielle (demonstration)', fontsize=11)
    pdf_bytes = cv.tobytes()
    tech.cv.save('CV_DEMONSTRATION.pdf', ContentFile(pdf_bytes), save=False)
    tech.photo.save('portrait_illustratif.png', ContentFile(image), save=False)
    tech.employee_number = 'CP-2026-00001'
    tech.birth_date = date(1994,4,12)
    tech.assignment_date = date(2026,9,1)
    tech.address = 'ADRESSE DE DEMONSTRATION'
    tech.experience = '<p><strong>2023 – 2026 · Technicien de maintenance industrielle</strong></p><ul><li>Maintenance préventive des pompes et équipements mécaniques.</li><li>Diagnostic des anomalies et rapports d’intervention.</li></ul><p><strong>2020 – 2023 · Technicien atelier</strong></p><p>Montage, inspection et remise en état des équipements.</p>'
    tech.save()
    tech2.employee_number='CP-2026-00002'
    tech2.specialty='ÉLECTROMÉCANIQUE'
    tech2.save()
    cert = pymupdf.open()
    cp=cert.new_page(); cp.insert_text((60,100),'CERTIFICAT DE DEMONSTRATION',fontsize=20)
    cp.insert_text((60,145),'Habilitation technique - document fictif',fontsize=12)
    doc=TechnicianCertificate(user=tech,name='Habilitation_DEMO.pdf')
    doc.file.save('Habilitation_DEMO.pdf',ContentFile(cert.tobytes()),save=True)
    approved=[]
    descriptions=['Maintenance préventive des pompes et contrôle des vibrations.',
        'Inspection des équipements et remplacement des éléments usés.',
        'Contrôle des alignements et rapport de fin d’intervention.',
        'Révision des ensembles mécaniques et essais de fonctionnement.',
        'Contrôle des dispositifs de sécurité et nettoyage technique.']
    for i in range(5):
        start=timezone.make_aware(datetime(2026,10,10+i,8))
        entry=TimeEntry.objects.create(technician=tech,project=p,start=start,end=start+timedelta(hours=8),description=descriptions[i])
        if i<4:
            transition_entry(entry.pk,tech,'submit')
        if i<3:
            transition_entry(entry.pk,manager,'approve'); approved.append(entry.pk)
    start=timezone.make_aware(datetime(2026,10,15,8))
    e=TimeEntry.objects.create(technician=tech2,project=p,start=start,end=start+timedelta(hours=7),description='Vérification des moteurs et câblages de commande.')
    transition_entry(e.pk,tech2,'submit')
    invoice=create_invoice(admin,p,approved[:2],date(2026,11,15),Decimal('0'))
    record_payment(admin,invoice=invoice,amount=Decimal('25000'),date=timezone.localdate(),method='TRANSFER',reference='VIR-DEMO-001')
    access_path.write_text(json.dumps({'password':password,'users':['demo-admin','demo-superviseur','demo-tech','demo-client']}),encoding='utf-8')
print('DEMO_READY: isolated database, synthetic records, API 127.0.0.1:8123',flush=True)
call_command('runserver','127.0.0.1:8123',use_reloader=False,verbosity=0)
