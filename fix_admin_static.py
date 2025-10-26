#!/usr/bin/env python
"""
🔧 Автоматическое исправление проблем с админкой Django на продакшене
"""
import os
import subprocess
import sys
from pathlib import Path
import shutil

def print_status(message, status="info"):
    """Вывод сообщения с иконкой"""
    icons = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️"}
    print(f"{icons.get(status, 'ℹ️')} {message}")

def run_command(command, description):
    """Выполняет команду и выводит результат"""
    print_status(f"Выполняем: {description}", "info")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print_status(f"Успешно: {description}", "success")
        if result.stdout:
            print(f"   Вывод: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Ошибка: {description}", "error")
        print(f"   Команда: {command}")
        print(f"   Код ошибки: {e.returncode}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False

def check_django_admin_static():
    """Проверяет наличие статических файлов Django admin"""
    staticfiles_dir = Path('staticfiles')
    admin_css = staticfiles_dir / 'admin' / 'css' / 'base.css'
    admin_js = staticfiles_dir / 'admin' / 'js'
    
    print_status("Проверка статических файлов админки...")
    
    if not staticfiles_dir.exists():
        print_status("Папка staticfiles не найдена", "error")
        return False
    
    if not admin_css.exists():
        print_status("CSS админки не найден", "error")
        return False
    
    if not admin_js.exists():
        print_status("JS админки не найден", "warning")
    
    print_status("Статические файлы админки найдены", "success")
    return True

def check_permissions():
    """Проверяет права доступа к статическим файлам"""
    print_status("Проверка прав доступа...")
    
    paths_to_check = ['static', 'staticfiles']
    for path_name in paths_to_check:
        if Path(path_name).exists():
            # Проверяем права доступа
            stat_info = Path(path_name).stat()
            permissions = oct(stat_info.st_mode)[-3:]
            print_status(f"{path_name}/ права: {permissions}")
            
            # Исправляем права если нужно
            if permissions != '755':
                print_status(f"Исправляем права для {path_name}/", "warning")
                os.chmod(path_name, 0o755)

def fix_static_url():
    """Исправляет STATIC_URL в settings.py если нужно"""
    settings_file = Path('mental/settings.py')
    
    if not settings_file.exists():
        print_status("Файл settings.py не найден", "error")
        return False
    
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, есть ли правильный STATIC_URL
    if "STATIC_URL = os.getenv('STATIC_URL', '/static/')" in content:
        print_status("STATIC_URL настроен правильно", "success")
        return True
    
    if "STATIC_URL = os.getenv('STATIC_URL', 'static/')" in content:
        print_status("Исправляем STATIC_URL в settings.py", "warning")
        content = content.replace(
            "STATIC_URL = os.getenv('STATIC_URL', 'static/')",
            "STATIC_URL = os.getenv('STATIC_URL', '/static/')"
        )
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print_status("STATIC_URL исправлен", "success")
        return True
    
    return True

def create_test_static_file():
    """Создает тестовый файл для проверки раздачи статики"""
    test_file = Path('staticfiles/test_static.txt')
    test_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(test_file, 'w') as f:
        f.write('Static files are working correctly!')
    
    print_status(f"Тестовый файл создан: {test_file}", "success")
    print_status("Проверьте по адресу: ваш-сайт.com/static/test_static.txt", "info")

def main():
    """Основная функция исправления проблем"""
    print("🚀 Исправление проблем с админкой Django на продакшене\n")
    
    # 1. Проверяем наличие manage.py
    if not Path('manage.py').exists():
        print_status("Файл manage.py не найден. Запустите скрипт из корня проекта", "error")
        sys.exit(1)
    
    # 2. Исправляем STATIC_URL
    fix_static_url()
    
    # 3. Собираем статические файлы
    if not run_command('python manage.py collectstatic --noinput', 'Сбор статических файлов'):
        print_status("Не удалось собрать статические файлы. Проверьте настройки Django", "error")
        sys.exit(1)
    
    # 4. Проверяем статические файлы админки
    if not check_django_admin_static():
        print_status("Статические файлы админки не найдены после collectstatic", "error")
        print_status("Возможно, проблема в настройках INSTALLED_APPS или STATICFILES_DIRS", "warning")
    
    # 5. Проверяем права доступа
    check_permissions()
    
    # 6. Создаем тестовый файл
    create_test_static_file()
    
    # 7. Финальные рекомендации
    print("\n🎉 Исправление завершено!")
    print("\n📝 Что нужно сделать дальше:")
    print("   1. Перезапустите веб-сервер (для Passenger: touch tmp/restart.txt)")
    print("   2. Очистите кэш браузера (Ctrl+F5)")
    print("   3. Проверьте админку: ваш-сайт.com/admin/")
    print("   4. Проверьте тестовый файл: ваш-сайт.com/static/test_static.txt")
    print("\n🔧 Если проблема не решена:")
    print("   - Проверьте логи веб-сервера")
    print("   - Убедитесь, что .htaccess правильно настроен")
    print("   - Обратитесь к STATIC_FILES_TROUBLESHOOTING.md")

if __name__ == '__main__':
    main()
