import os
from decouple import config

# Determine which settings to use based on environment
environment = config('DJANGO_SETTINGS_MODULE', default='Acta_backend.settings.development')

if 'production' in environment:
    from .production import *
elif 'development' in environment:
    from .development import *
else:
    from .base import *
