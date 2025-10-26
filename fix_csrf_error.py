#!/usr/bin/env python
"""
🔧 Исправление ошибки CSRF 403 на продакшене Django
"""
import os
import sys
from pathlib import Path

def print_status(message, status="info"):
    """Вывод сообщения с иконкой"""
    icons = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️"}
    print(f"{icons.get(status, 'ℹ️')} {message}")

def check_env_file():
    """Проверяет наличие и содержимое .env файла"""
    print_status("Проверка файла .env...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print_status("Файл .env не найден, создаем из env_production.txt", "warning")
        production_env = Path('env_production.txt')
        if production_env.exists():
            import shutil
            shutil.copy('env_production.txt', '.env')
            print_status("Файл .env создан из env_production.txt", "success")
        else:
            print_status("Файл env_production.txt не найден", "error")
            return False
    
    # Читаем .env файл
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            env_content = f.read()
        
        print_status("Содержимое .env файла:", "info")
        for line in env_content.splitlines():
            if line.strip() and not line.startswith('#'):
                print(f"   {line}")
        
        return True
    except Exception as e:
        print_status(f"Ошибка чтения .env: {e}", "error")
        return False

def get_current_domain():
    """Пытается определить текущий домен"""
    possible_domains = []
    
    # Проверяем переменные окружения
    if 'HTTP_HOST' in os.environ:
        possible_domains.append(os.environ['HTTP_HOST'])
    
    if 'SERVER_NAME' in os.environ:
        possible_domains.append(os.environ['SERVER_NAME'])
    
    # Проверяем файлы конфигурации
    try:
        import subprocess
        result = subprocess.run(['hostname', '-f'], capture_output=True, text=True)
        if result.returncode == 0:
            hostname = result.stdout.strip()
            if hostname:
                possible_domains.append(hostname)
    except:
        pass
    
    return possible_domains

def update_env_file():
    """Обновляет .env файл с правильными настройками"""
    print_status("Обновление .env файла...")
    
    domains = get_current_domain()
    print_status(f"Обнаружены возможные домены: {domains}")
    
    # Читаем текущий .env
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = ""
    
    # Добавляем необходимые настройки
    updates = []
    
    if 'ALLOWED_HOSTS=' not in content:
        hosts = ['localhost', '127.0.0.1']
        hosts.extend(domains)
        updates.append(f"ALLOWED_HOSTS={','.join(set(hosts))}")
    
    if 'MAIN_DOMAIN=' not in content and domains:
        updates.append(f"MAIN_DOMAIN={domains[0]}")
    
    if 'CSRF_COOKIE_SECURE=' not in content:
        updates.append("CSRF_COOKIE_SECURE=False")
    
    if 'SESSION_COOKIE_SECURE=' not in content:
        updates.append("SESSION_COOKIE_SECURE=False")
    
    if updates:
        with open(env_file, 'a', encoding='utf-8') as f:
            f.write('\n# Автоматически добавленные настройки для исправления CSRF\n')
            for update in updates:
                f.write(f"{update}\n")
        
        print_status("Файл .env обновлен", "success")
        for update in updates:
            print(f"   Добавлено: {update}")
    else:
        print_status("Файл .env уже содержит необходимые настройки", "success")

def restart_server():
    """Перезапускает сервер"""
    print_status("Перезапуск сервера...")
    
    # Для Passenger
    tmp_dir = Path('tmp')
    tmp_dir.mkdir(exist_ok=True)
    restart_file = tmp_dir / 'restart.txt'
    restart_file.touch()
    print_status("Сервер перезапущен (Passenger)", "success")
    
    print_status("Если используете другой сервер, перезапустите его вручную", "info")

def create_csrf_debug_view():
    """Создает временный view для отладки CSRF"""
    debug_view = '''
# Временный view для отладки CSRF - добавьте в urls.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@csrf_exempt
def csrf_debug(request):
    """Отладочная информация по CSRF"""
    return JsonResponse({
        'DEBUG': settings.DEBUG,
        'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
        'CSRF_COOKIE_SECURE': getattr(settings, 'CSRF_COOKIE_SECURE', None),
        'SESSION_COOKIE_SECURE': getattr(settings, 'SESSION_COOKIE_SECURE', None),
        'CSRF_TRUSTED_ORIGINS': getattr(settings, 'CSRF_TRUSTED_ORIGINS', []),
        'HTTP_HOST': request.META.get('HTTP_HOST'),
        'SERVER_NAME': request.META.get('SERVER_NAME'),
        'HTTP_X_FORWARDED_HOST': request.META.get('HTTP_X_FORWARDED_HOST'),
    })

# Добавьте в urls.py:
# path('debug/csrf/', csrf_debug, name='csrf_debug'),
'''
    
    with open('csrf_debug_view.py', 'w', encoding='utf-8') as f:
        f.write(debug_view)
    
    print_status("Создан файл csrf_debug_view.py для отладки", "success")

def main():
    """Основная функция исправления CSRF ошибок"""
    print("🔧 Исправление ошибки CSRF 403 на продакшене\n")
    
    # Проверяем, что мы в корне проекта Django
    if not Path('manage.py').exists():
        print_status("Файл manage.py не найден. Запустите из корня проекта Django", "error")
        sys.exit(1)
    
    # 1. Проверяем .env файл
    check_env_file()
    
    # 2. Обновляем .env с правильными настройками
    update_env_file()
    
    # 3. Перезапускаем сервер
    restart_server()
    
    # 4. Создаем отладочный view
    create_csrf_debug_view()
    
    print("\n🎉 Исправления применены!")
    print("\n📝 Что делать дальше:")
    print("   1. Проверьте, что домен в ALLOWED_HOSTS правильный")
    print("   2. Очистите кэш браузера (Ctrl+F5)")
    print("   3. Попробуйте снова зайти в админку")
    print("   4. Для отладки добавьте в urls.py:")
    print("      path('debug/csrf/', csrf_debug, name='csrf_debug')")
    print("      и откройте /debug/csrf/ для просмотра настроек")
    print("\n🔧 Если ошибка остается:")
    print("   - Проверьте правильность домена в настройках хостинга")
    print("   - Убедитесь, что файл .env загружается корректно")
    print("   - Проверьте логи веб-сервера")

if __name__ == '__main__':
    main()
