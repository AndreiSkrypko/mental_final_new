import sys
import os

# Путь к корневой папке проекта
sys.path.insert(0, '/home/robotlidab/math')

# Указываем модуль настроек Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'mental.settings'

# Подключаем WSGI-приложение
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
