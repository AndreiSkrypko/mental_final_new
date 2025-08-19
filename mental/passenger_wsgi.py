import sys
import os

# Путь к проекту
sys.path.insert(0, '/home/robotlidab/public_html/mental.robotlida.by')

os.environ['DJANGO_SETTINGS_MODULE'] = 'mental.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
