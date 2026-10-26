"""Run the workflow suite in a new disposable MySQL database, never in copet."""
import configparser
import os
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coproject.settings')

import django
from django.conf import settings
from django.test.utils import get_runner

admin = configparser.ConfigParser(interpolation=None)
admin.read(ROOT / '.runtime/mysql-admin.cnf', encoding='utf-8')
settings.DATABASES['default'].update({
    'HOST': '127.0.0.1', 'PORT': '3308', 'USER': 'root', 'PASSWORD': admin['client']['password'],
    'TEST': {'NAME': 'test_copet_' + uuid.uuid4().hex[:12]},
})
settings.PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
django.setup()
runner = get_runner(settings)(verbosity=1, interactive=False)
sys.exit(bool(runner.run_tests(['eliteapp'])))
