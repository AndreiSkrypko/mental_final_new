#!/usr/bin/env python
"""
Тест добавления ученика через класс
Проверяет сценарий, который вызывает 500 ошибку на сервере
"""

import os
import sys
import django
from django.conf import settings

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mental.settings')
django.setup()

from mental_app.models import Students, Class, TeacherProfile, User
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from mental_app.views import student_create
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.messages import get_messages

def test_student_creation_in_class():
    """Тестирует создание ученика через класс (с class_id)"""
    print("=== Тест создания ученика через класс ===")
    
    try:
        # Проверяем наличие учителей
        teachers = TeacherProfile.objects.filter(status='approved')
        if not teachers.exists():
            print("❌ Нет подтвержденных учителей в системе")
            return False
        
        teacher = teachers.first()
        print(f"✅ Найден учитель: {teacher.user.username}")
        
        # Проверяем наличие классов у учителя
        classes = Class.objects.filter(teacher=teacher)
        if not classes.exists():
            print("❌ У учителя нет классов")
            return False
        
        class_obj = classes.first()
        print(f"✅ Найден класс: {class_obj.name}")
        
        # Создаем тестовый запрос
        factory = RequestFactory()
        
        # Создаем POST запрос с данными ученика
        post_data = {
            'name': 'ТестКласс',
            'surname': 'УченикКласс',
            'age': '12',
            'parent_first_name': 'Тест',
            'parent_last_name': 'Родитель',
            'parent_phone_number': '+375291234567'
        }
        
        request = factory.post(f'/teacher/classes/{class_obj.id}/students/create/', post_data)
        
        # Устанавливаем пользователя
        request.user = teacher.user
        
        # Настраиваем сообщения
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        print(f"📝 Тестируем создание ученика в классе {class_obj.id}")
        print(f"📊 Данные запроса: {post_data}")
        
        # Вызываем представление
        response = student_create(request, class_id=class_obj.id)
        
        print(f"📤 Ответ: {response}")
        
        if hasattr(response, 'status_code'):
            print(f"📊 Код ответа: {response.status_code}")
        
        # Проверяем, создался ли ученик
        try:
            student = Students.objects.get(
                name='ТестКласс',
                surname='УченикКласс',
                student_class=class_obj
            )
            print(f"✅ Ученик успешно создан в классе: {student}")
            
            # Удаляем тестового ученика
            student.delete()
            print("✅ Тестовый ученик удален")
            
            return True
            
        except Students.DoesNotExist:
            print("❌ Ученик не был создан")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_student_creation_without_class():
    """Тестирует создание ученика без класса (без class_id)"""
    print("\n=== Тест создания ученика без класса ===")
    
    try:
        teachers = TeacherProfile.objects.filter(status='approved')
        if not teachers.exists():
            print("❌ Нет подтвержденных учителей в системе")
            return False
        
        teacher = teachers.first()
        print(f"✅ Найден учитель: {teacher.user.username}")
        
        # Создаем тестовый запрос
        factory = RequestFactory()
        
        post_data = {
            'name': 'ТестБезКласса',
            'surname': 'УченикБезКласса',
            'age': '10',
            'parent_first_name': 'Тест',
            'parent_last_name': 'Родитель',
            'parent_phone_number': '+375291234567'
        }
        
        request = factory.post('/teacher/students/create/', post_data)
        request.user = teacher.user
        
        # Настраиваем сообщения
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        print(f"📝 Тестируем создание ученика без класса")
        print(f"📊 Данные запроса: {post_data}")
        
        # Вызываем представление
        response = student_create(request, class_id=None)
        
        print(f"📤 Ответ: {response}")
        
        if hasattr(response, 'status_code'):
            print(f"📊 Код ответа: {response.status_code}")
        
        # Проверяем, создался ли ученик
        try:
            student = Students.objects.get(
                name='ТестБезКласса',
                surname='УченикБезКласса'
            )
            print(f"✅ Ученик успешно создан без класса: {student}")
            
            # Удаляем тестового ученика
            student.delete()
            print("✅ Тестовый ученик удален")
            
            return True
            
        except Students.DoesNotExist:
            print("❌ Ученик не был создан")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Тестирует подключение к базе данных"""
    print("=== Тест подключения к базе данных ===")
    
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"✅ Подключение к БД: {result}")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {str(e)}")
        return False

def test_models_integrity():
    """Тестирует целостность моделей"""
    print("=== Тест целостности моделей ===")
    
    try:
        # Проверяем, что модели можно импортировать
        from mental_app.models import Students, Class, TeacherProfile
        
        # Проверяем, что можно создавать объекты
        teacher_count = TeacherProfile.objects.count()
        class_count = Class.objects.count()
        student_count = Students.objects.count()
        
        print(f"✅ Учителей в БД: {teacher_count}")
        print(f"✅ Классов в БД: {class_count}")
        print(f"✅ Учеников в БД: {student_count}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка проверки моделей: {str(e)}")
        return False

if __name__ == '__main__':
    print("🚀 Запуск тестов создания ученика...")
    
    # Тестируем базовое подключение
    if not test_database_connection():
        print("❌ Не удалось подключиться к базе данных")
        sys.exit(1)
    
    if not test_models_integrity():
        print("❌ Проблемы с моделями")
        sys.exit(1)
    
    # Тестируем создание ученика без класса
    success1 = test_student_creation_without_class()
    
    # Тестируем создание ученика через класс
    success2 = test_student_creation_in_class()
    
    print("\n" + "="*50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"✅ Создание без класса: {'УСПЕХ' if success1 else 'ОШИБКА'}")
    print(f"✅ Создание через класс: {'УСПЕХ' if success2 else 'ОШИБКА'}")
    
    if success1 and success2:
        print("🎉 Все тесты прошли успешно!")
    else:
        print("⚠️  Некоторые тесты не прошли")
        if not success2:
            print("🔍 Проблема именно в создании ученика через класс!")
    
    print("="*50)
