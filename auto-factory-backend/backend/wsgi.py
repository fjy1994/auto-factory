"""
WSGI config for auto-factory-backend project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto-factory-backend.settings')

application = get_wsgi_application()
