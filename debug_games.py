#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mental.settings')
django.setup()

from mental_app.models import Class, ClassGameAccess, Students

def debug_games():
    print("=== ОТЛАДКА СИСТЕМЫ ИГР ===\n")
    
    # Проверяем все классы
    print("1. Все классы:")
    classes = Class.objects.all()
    for cls in classes:
        print(f"   - {cls.name} (учитель: {cls.teacher.user.get_full_name()})")
    
    print("\n2. Настройки игр для каждого класса:")
    for cls in classes:
        print(f"\n   Класс: {cls.name}")
        game_accesses = ClassGameAccess.objects.filter(class_group=cls)
        if game_accesses.exists():
            for access in game_accesses:
                status = "✅ ВКЛ" if access.is_enabled else "❌ ВЫКЛ"
                print(f"     {access.get_game_display()}: {status}")
        else:
            print("     Нет настроек игр")
    
    print("\n3. Ученики и их классы:")
    students = Students.objects.all()
    for student in students:
        class_name = student.student_class.name if student.student_class else "Без класса"
        print(f"   - {student.surname} {student.name} -> {class_name}")
    
    print("\n4. Проверка доступности игр для учеников:")
    for student in students:
        if student.student_class:
            print(f"\n   Ученик: {student.surname} {student.name}")
            print(f"   Класс: {student.student_class.name}")
            
            # Получаем доступные игры
            class_games = ClassGameAccess.objects.filter(
                class_group=student.student_class,
                is_enabled=True
            )
            
            if class_games.exists():
                print("   Доступные игры:")
                for game_access in class_games:
                    print(f"     - {game_access.get_game_display()}")
            else:
                print("   ❌ Нет доступных игр")
        else:
            print(f"   {student.surname} {student.name} -> без класса")

if __name__ == '__main__':
    debug_games()
