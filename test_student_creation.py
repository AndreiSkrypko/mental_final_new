#!/usr/bin/env python
"""
Скрипт для тестирования создания ученика
Запускать из корня проекта: python test_student_creation.py
"""

import os
import sys
import django
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mental.settings')
django.setup()

from mental_app.models import Students, Class, TeacherProfile
from django.contrib.auth.models import User

def test_student_creation():
    """Тестирует создание ученика"""
    print("=== Тест создания ученика ===")
    
    try:
        # Проверяем, есть ли учителя в системе
        teachers = TeacherProfile.objects.all()
        print(f"Найдено учителей: {teachers.count()}")
        
        if teachers.count() == 0:
            print("❌ Нет учителей в системе. Создайте учителя сначала.")
            return False
        
        # Берем первого одобренного учителя
        teacher = teachers.filter(status='approved').first()
        if not teacher:
            print("❌ Нет одобренных учителей в системе.")
            return False
        
        print(f"✅ Используем учителя: {teacher.user.username}")
        
        # Проверяем, есть ли классы у учителя
        classes = Class.objects.filter(teacher=teacher)
        print(f"Найдено классов у учителя: {classes.count()}")
        
        if classes.count() == 0:
            print("❌ У учителя нет классов. Создайте класс сначала.")
            return False
        
        # Берем первый класс
        class_obj = classes.first()
        print(f"✅ Используем класс: {class_obj.name}")
        
        # Создаем тестового ученика
        student_data = {
            'name': 'Тест',
            'surname': 'Ученик',
            'age': 10,
            'parent_first_name': 'Тест',
            'parent_last_name': 'Родитель',
            'parent_phone_number': '+375291234567',
            'student_class': class_obj
        }
        
        print(f"Создаем ученика: {student_data}")
        
        # Создаем ученика
        student = Students.objects.create(**student_data)
        print(f"✅ Ученик успешно создан: {student}")
        
        # Проверяем, что ученик сохранился в базе
        saved_student = Students.objects.get(id=student.id)
        print(f"✅ Ученик найден в базе: {saved_student}")
        
        # Удаляем тестового ученика
        student.delete()
        print("✅ Тестовый ученик удален")
        
        return True
        
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
        print(f"✅ Подключение к БД успешно: {result}")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {str(e)}")
        return False

def test_models():
    """Тестирует модели"""
    print("=== Тест моделей ===")
    
    try:
        # Проверяем модель Students
        students_count = Students.objects.count()
        print(f"✅ Модель Students работает. Количество учеников: {students_count}")
        
        # Проверяем модель Class
        classes_count = Class.objects.count()
        print(f"✅ Модель Class работает. Количество классов: {classes_count}")
        
        # Проверяем модель TeacherProfile
        teachers_count = TeacherProfile.objects.count()
        print(f"✅ Модель TeacherProfile работает. Количество учителей: {teachers_count}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка при тестировании моделей: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"Запуск тестов в {datetime.now()}")
    print("=" * 50)
    
    # Запускаем тесты
    db_ok = test_database_connection()
    models_ok = test_models()
    
    if db_ok and models_ok:
        student_ok = test_student_creation()
        if student_ok:
            print("\n🎉 Все тесты прошли успешно!")
        else:
            print("\n⚠️ Тесты моделей прошли, но создание ученика не удалось")
    else:
        print("\n❌ Базовые тесты не прошли")
    
    print("=" * 50)
