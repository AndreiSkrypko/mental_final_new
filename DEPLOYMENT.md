# Инструкция по деплою Django проекта

## 1. Подготовка переменных среды

Создайте файл `.env` в корне проекта на основе `env_example.txt`:

```bash
cp env_example.txt .env
```

Отредактируйте `.env` файл, указав реальные значения:

```env
# Django settings
DEBUG=False
SECRET_KEY=ваш-секретный-ключ-здесь
ALLOWED_HOSTS=ваш-домен.com,www.ваш-домен.com

# Database settings (для PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Static and media files
STATIC_URL=/static/
MEDIA_URL=/media/

# Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=ваш-email@gmail.com
EMAIL_HOST_PASSWORD=ваш-пароль-приложения

# Security settings
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
```

## 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

## 3. Сбор статических файлов

```bash
python manage.py collectstatic
```

## 4. Миграции базы данных

```bash
python manage.py migrate
```

## 5. Создание суперпользователя

```bash
python manage.py createsuperuser
```

## 6. Настройка веб-сервера

### Для Nginx + Gunicorn:

Создайте файл `gunicorn.conf.py`:

```python
bind = "127.0.0.1:8000"
workers = 3
user = "www-data"
group = "www-data"
```

### Для systemd сервиса:

Создайте файл `/etc/systemd/system/mental.service`:

```ini
[Unit]
Description=Mental Arithmetic Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/mental_arifmetic
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn --config gunicorn.conf.py mental.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

## 7. Переменные среды для разных окружений

### Development (.env.development):
```env
DEBUG=True
SECRET_KEY=dev-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Production (.env.production):
```env
DEBUG=False
SECRET_KEY=production-secret-key
ALLOWED_HOSTS=ваш-домен.com
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
```

## 8. Проверка безопасности

Перед деплоем в продакшн:

1. Убедитесь, что `DEBUG=False`
2. Измените `SECRET_KEY`
3. Настройте `ALLOWED_HOSTS`
4. Включите HTTPS
5. Настройте бэкапы базы данных

## 9. Мониторинг

Добавьте логирование в `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/mental.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```
