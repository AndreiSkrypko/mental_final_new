import sys, os

# Путь к проекту
sys.path.insert(0, '/home/robotlidab/mental_robotlida')

# Настройки Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'mental.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()