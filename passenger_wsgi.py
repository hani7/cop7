"""Passenger entry point for the Django application on cPanel."""

import os
import sys

# Resolve the project from the deployed cPanel application directory while
# retaining the file location as a portable fallback for local execution.
DEPLOYED_ROOT = '/home/copetr70/copus'
BASE_DIR = os.environ.get('APP_ROOT') or (
    DEPLOYED_ROOT if os.path.isdir(DEPLOYED_ROOT) else os.path.dirname(os.path.abspath(__file__))
)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coproject.settings')

from coproject.wsgi import application

