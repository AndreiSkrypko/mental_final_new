#!/usr/bin/env python3
"""
Тест для проверки новой логики генерации чисел в игре.
Проверяем, что промежуточная сумма никогда не становится отрицательной.
"""

import random

def generate_numbers_old_logic(num_examples=10, max_digit=9, range_key=2):
    """Старая логика - простое чередование знаков"""
    # Определяем диапазон чисел
    if range_key == 1:
        min_num, max_num = 1, 10
    elif range_key == 2:
        min_num, max_num = 10, 100
    elif range_key == 3:
        min_num, max_num = 100, 1000
    elif range_key == 4:
        min_num, max_num = 1000, 10000
    else:
        min_num, max_num = 10, 100
    
    numbers = []
    available_digits = list(range(1, max_digit + 1))
    current_sign = 1  # Начинаем с положительного
    
    for i in range(num_examples):
        # Определяем количество разрядов для числа
        if range_key == 1:
            num_digits = 1
        elif range_key == 2:
            num_digits = 2
        elif range_key == 3:
            num_digits = 3
        elif range_key == 4:
            num_digits = 4
        else:
            num_digits = 2
        
        # Генерируем число по разрядам
        number = 0
        for digit_pos in range(num_digits):
            digit = random.choice(available_digits)
            number += digit * (10 ** (num_digits - 1 - digit_pos))
        
        if min_num <= number <= max_num:
            # Старая логика - просто чередуем знаки
            number *= current_sign
            current_sign = -current_sign  # Меняем знак для следующего числа
            numbers.append(number)
        else:
            i -= 1
            continue
    
    return numbers

def generate_numbers_new_logic(num_examples=10, max_digit=9, range_key=2):
    """Новая логика - проверяем промежуточную сумму"""
    # Определяем диапазон чисел
    if range_key == 1:
        min_num, max_num = 1, 10
    elif range_key == 2:
        min_num, max_num = 10, 100
    elif range_key == 3:
        min_num, max_num = 100, 1000
    elif range_key == 4:
        min_num, max_num = 1000, 10000
    else:
        min_num, max_num = 10, 100
    
    numbers = []
    available_digits = list(range(1, max_digit + 1))
    current_sum = 0
    
    for i in range(num_examples):
        # Определяем количество разрядов для числа
        if range_key == 1:
            num_digits = 1
        elif range_key == 2:
            num_digits = 2
        elif range_key == 3:
            num_digits = 3
        elif range_key == 4:
            num_digits = 4
        else:
            num_digits = 2
        
        # Генерируем число по разрядам
        number = 0
        for digit_pos in range(num_digits):
            digit = random.choice(available_digits)
            number += digit * (10 ** (num_digits - 1 - digit_pos))
        
        if min_num <= number <= max_num:
            # Новая логика - проверяем промежуточную сумму
            if i == 0:
                # Первое число всегда положительное
                sign = 1
            else:
                # Для последующих чисел проверяем, можно ли сделать отрицательным
                if current_sum >= number:
                    # Можем выбрать любой знак
                    sign = random.choice([-1, 1])
                else:
                    # Можем только положительный знак
                    sign = 1
            
            final_number = number * sign
            numbers.append(final_number)
            current_sum += final_number
        else:
            i -= 1
            continue
    
    return numbers

def check_intermediate_sums(numbers):
    """Проверяем, что все промежуточные суммы неотрицательные"""
    current_sum = 0
    intermediate_sums = []
    
    for i, num in enumerate(numbers):
        current_sum += num
        intermediate_sums.append(current_sum)
        if current_sum < 0:
            return False, i, intermediate_sums
    
    return True, -1, intermediate_sums

def test_logic():
    """Тестируем обе логики"""
    print("=== ТЕСТ ГЕНЕРАЦИИ ЧИСЕЛ ===\n")
    
    # Тестируем несколько раз
    test_cases = 100
    old_logic_failures = 0
    new_logic_failures = 0
    
    print("Тестируем старую логику:")
    for i in range(test_cases):
        numbers = generate_numbers_old_logic(num_examples=10, max_digit=9, range_key=2)
        is_valid, fail_index, sums = check_intermediate_sums(numbers)
        if not is_valid:
            old_logic_failures += 1
            if old_logic_failures <= 3:  # Показываем только первые 3 примера
                print(f"  Пример {i+1}: Отрицательная сумма на позиции {fail_index}")
                print(f"    Числа: {numbers[:fail_index+1]}")
                print(f"    Промежуточные суммы: {sums[:fail_index+1]}")
    
    print(f"\nСтарая логика: {old_logic_failures} из {test_cases} тестов с отрицательными суммами\n")
    
    print("Тестируем новую логику:")
    for i in range(test_cases):
        numbers = generate_numbers_new_logic(num_examples=10, max_digit=9, range_key=2)
        is_valid, fail_index, sums = check_intermediate_sums(numbers)
        if not is_valid:
            new_logic_failures += 1
            if new_logic_failures <= 3:  # Показываем только первые 3 примера
                print(f"  Пример {i+1}: Отрицательная сумма на позиции {fail_index}")
                print(f"    Числа: {numbers[:fail_index+1]}")
                print(f"    Промежуточные суммы: {sums[:fail_index+1]}")
    
    print(f"\nНовая логика: {new_logic_failures} из {test_cases} тестов с отрицательными суммами\n")
    
    # Показываем несколько примеров новой логики
    print("Примеры работы новой логики:")
    for i in range(3):
        numbers = generate_numbers_new_logic(num_examples=8, max_digit=9, range_key=2)
        is_valid, fail_index, sums = check_intermediate_sums(numbers)
        print(f"\nПример {i+1}:")
        print(f"  Числа: {numbers}")
        print(f"  Промежуточные суммы: {sums}")
        print(f"  Итоговая сумма: {sum(numbers)}")
        print(f"  Все суммы неотрицательные: {'✓' if is_valid else '✗'}")

if __name__ == "__main__":
    test_logic()
