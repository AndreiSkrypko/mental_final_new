#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mental.settings')
django.setup()

from mental_app.models import Class, ClassGameAccess, Students

def debug_games_detailed():
    print("=== ДЕТАЛЬНАЯ ОТЛАДКА СИСТЕМЫ ИГР ===\n")
    
    # Проверяем все классы
    print("1. Все классы:")
    classes = Class.objects.all()
    for cls in classes:
        print(f"   - ID: {cls.id}, Название: {cls.name}, Учитель: {cls.teacher.user.get_full_name()}")
    
    print("\n2. ВСЕ записи в ClassGameAccess:")
    all_game_access = ClassGameAccess.objects.all()
    for access in all_game_access:
        status = "✅ ВКЛ" if access.is_enabled else "❌ ВЫКЛ"
        print(f"   - ID: {access.id}, Класс: {access.class_group.name}, Игра: {access.game} ({access.get_game_display()}) -> {status}")
    
    print("\n3. Настройки игр для каждого класса:")
    for cls in classes:
        print(f"\n   Класс: {cls.name} (ID: {cls.id})")
        game_accesses = ClassGameAccess.objects.filter(class_group=cls)
        if game_accesses.exists():
            for access in game_accesses:
                status = "✅ ВКЛ" if access.is_enabled else "❌ ВЫКЛ"
                print(f"     {access.game} -> {access.get_game_display()}: {status}")
        else:
            print("     Нет настроек игр")
    
    print("\n4. Ученики и их классы:")
    students = Students.objects.all()
    for student in students:
        if student.student_class:
            class_name = f"{student.student_class.name} (ID: {student.student_class.id})"
        else:
            class_name = "Без класса"
        print(f"   - {student.surname} {student.name} -> {class_name}")
    
    print("\n5. Проверка доступности игр для учеников:")
    for student in students:
        if student.student_class:
            print(f"\n   Ученик: {student.surname} {student.name}")
            print(f"   Класс: {student.student_class.name} (ID: {student.student_class.id})")
            
            # Получаем доступные игры
            class_games = ClassGameAccess.objects.filter(
                class_group=student.student_class,
                is_enabled=True
            )
            
            if class_games.exists():
                print("   Доступные игры:")
                for game_access in class_games:
                    print(f"     - {game_access.game} -> {game_access.get_game_display()}")
            else:
                print("   ❌ Нет доступных игр")
        else:
            print(f"   {student.surname} {student.name} -> без класса")

if __name__ == '__main__':
    debug_games_detailed()
