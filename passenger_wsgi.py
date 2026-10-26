"""Passenger entry point for the Django application on cPanel."""

import os
import sys

# Passenger loads this file from the application root. Using its actual
# location keeps the WSGI entry point portable across local and cPanel runs.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coproject.settings')

from coproject.wsgi import application

