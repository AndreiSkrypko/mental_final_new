import random
import time
import logging
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseServerError
from django.utils import timezone
from functools import wraps
from .models import (
    Students, Class, TeacherProfile, StudentAccount, 
    Homework, PaymentSettings, ClassGameAccess, 
    Attendance, GameSettings, MonthlySchedule
)
from .forms import StudentForm, TeacherRegistrationForm, TeacherLoginForm, ClassForm, TeacherProfileUpdateForm, StudentAccountForm, StudentLoginForm, HomeworkForm, AttendanceForm, AttendanceDateForm, PaymentSettingsForm, MonthlyScheduleForm, MonthlyAttendanceForm

# Логгер для ошибок
logger = logging.getLogger(__name__)

def handle_errors(view_func):
    """Декоратор для обработки ошибок в представлениях"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка в представлении {view_func.__name__}: {str(e)}", exc_info=True)
            if request.is_ajax():
                return JsonResponse({'error': 'Произошла ошибка сервера'}, status=500)
            return HttpResponseServerError(render(request, '500.html'))
    return wrapper

# Определяем словарь диапазонов чисел
RANGES = {
    '1-9': list(range(1, 10)),
    '10-19': list(range(10, 19)),
    '20-29': list(range(20, 29)),
    '30-70': list(range(30, 70)),
    '80-120': list(range(80, 120)),
    '10-99': list(range(10, 100)),
    '100-999': list(range(100, 1000)),
    '1000-9999': list(range(1000, 10000)),
    '10000-99999': list(range(10000, 100000)),
    '10': list(range(1, 10)),
    '50': list(range(1, 50)),
    '100': list(range(1, 100)),
    '200': list(range(1, 200)),
    '1000': list(range(1, 1000)),
    'random': list(range(1, 101)),
    'both-lower': list(range(1, 51)),
    'one-lower-one-higher': list(range(1, 101)),
    'both-higher': list(range(50, 151)),
    '2-9': list(range(2, 10)),
    "1-10": list(range(1, 10)),
    "10-100": list(range(10, 100)),
    "100-1000": list(range(100, 1000)),
    "1000-10000": list(range(1000, 10000)),
}


# Обработчик главной страницы
@handle_errors
def index(request):
    if request.method == 'GET':  # Если запрос GET
        return render(request, 'index.html')  # Отображаем шаблон index.html
    if request.method == 'POST':  # Если запрос POST (но пока не обработан)
        pass  # Ничего не делаем


# Обработчик выбора и проверки умножения
def multiplication_choose(request, mode):
    # Проверяем авторизацию ученика или учителя
    if not request.session.get('student_id') and not (hasattr(request.user, 'teacher_profile') and request.user.teacher_profile.status == 'approved'):
        return redirect('student_login')
    
    if mode == 1:  # Этап выбора чисел
        if request.method == 'GET':  # Если запрос GET
            return render(request, 'multiplication_choose.html', {"mode": 1})  # Отображаем форму выбора чисел

        if request.method == 'POST':  # Если запрос POST
            # Получаем выбранные диапазоны чисел из формы
            first_multiplier_range = request.POST.get('first-multiplier')
            second_multiplier_range = request.POST.get('second-multiplier')

            # Получаем списки чисел из словаря RANGES
            first_multipliers = RANGES.get(first_multiplier_range, [])
            second_multipliers = RANGES.get(second_multiplier_range, [])

            # Если хотя бы один список пустой, перенаправляем пользователя обратно
            if not first_multipliers or not second_multipliers:
                return redirect('multiplication_choose', mode=1)

            # Сохраняем диапазоны и случайные числа в сессии
            request.session['first_multiplier_range'] = first_multiplier_range
            request.session['second_multiplier_range'] = second_multiplier_range
            
            first = random.choice(first_multipliers)  # Случайное число из первого списка
            second = random.choice(second_multipliers)  # Случайное число из второго списка
            
            # Случайно выбираем знак для чисел
            first_sign = random.choice([-1, 1])
            second_sign = random.choice([-1, 1])
            
            first *= first_sign
            second *= second_sign
            
            request.session['first'] = first
            request.session['second'] = second

            # Переход на следующий этап (отображение примера)
            return redirect('multiplication_choose', mode=2)

    elif mode == 2:  # Этап отображения примера
        first = request.session.get('first')  # Получаем первое число из сессии
        second = request.session.get('second')  # Получаем второе число из сессии

        # Если чисел нет в сессии, возвращаем пользователя на этап выбора
        if first is None or second is None:
            return redirect('multiplication_choose', mode=1)

        # Отображаем шаблон с примером для умножения
        return render(request, 'multiplication_choose.html', {
            'first': first,
            'second': second,
            'operation': '×',  # Знак умножения
            'mode': 2
        })

    elif mode == 3:  # Этап проверки ответа
        first = request.session.get('first')  # Получаем первое число
        second = request.session.get('second')  # Получаем второе число
        first_multiplier_range = request.session.get('first_multiplier_range')  # Получаем диапазон первого числа
        second_multiplier_range = request.session.get('second_multiplier_range')  # Получаем диапазон второго числа

        if request.method == 'POST':  # Если запрос POST
            user_answer = request.POST.get('user-answer')  # Получаем ответ пользователя
            correct_answer = first * second  # Вычисляем правильный ответ

            if user_answer and user_answer.isdigit() and int(user_answer) == correct_answer:
                result_message = "Верно! Молодец!"  # Сообщение о правильном ответе
                result_color = "green"  # Цвет сообщения

                # Генерируем новый пример
                first_multipliers = RANGES.get(first_multiplier_range,
                                               [])  # Получаем список чисел для первого множителя
                second_multipliers = RANGES.get(second_multiplier_range,
                                                [])  # Получаем список чисел для второго множителя

                if first_multipliers and second_multipliers:
                    new_first = random.choice(first_multipliers)  # Случайное число для нового примера
                    new_second = random.choice(second_multipliers)  # Случайное число для нового примера
                    
                    # Случайно выбираем знак для новых чисел
                    first_sign = random.choice([-1, 1])
                    second_sign = random.choice([-1, 1])
                    
                    new_first *= first_sign
                    new_second *= second_sign
                    
                    request.session['first'] = new_first
                    request.session['second'] = new_second
            else:
                result_message = "Неверно! Попробуйте снова."  # Сообщение о неверном ответе
                result_color = "red"  # Цвет сообщения

            # Отображаем шаблон с результатом проверки
            return render(request, 'multiplication_choose.html', {
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'result': result_message,
                'result_color': result_color,
                'mode': 3
            })

        # Если запрос GET, возвращаем пользователя на предыдущий этап (отображение примера)
        return redirect('multiplication_choose', mode=2)


# Обработчик выбора и проверки умножения до 20
def multiplication_to_20(request, mode):
    # Проверяем авторизацию ученика или учителя
    if not request.session.get('student_id') and not (hasattr(request.user, 'teacher_profile') and request.user.teacher_profile.status == 'approved'):
        return redirect('student_login')
    
    if mode == 1:  # Этап выбора чисел
        if request.method == 'GET':  # Если запрос GET
            return render(request, 'multiplication_to_20.html', {"mode": 1})  # Отображаем форму выбора чисел

        if request.method == 'POST':  # Если запрос POST
            # Получаем выбранные диапазоны чисел из формы
            first_multiplier_range = request.POST.get('first-multiplier')  # Диапазон первого множителя
            second_multiplier_value = request.POST.get('second-multiplier')  # Значение второго множителя (не диапазон)

            # Получаем список чисел для первого множителя из словаря RANGES
            first_multipliers = RANGES.get(first_multiplier_range, [])

            # Для второго множителя просто сохраняем значение, так как оно не из списка
            try:
                second_multiplier = int(second_multiplier_value)  # Преобразуем значение второго множителя в число
            except ValueError:
                second_multiplier = None  # Если значение не число, сохраняем как None

            # Если хотя бы одно число пустое или второй множитель вне диапазона 1-20, перенаправляем обратно
            if not first_multipliers or second_multiplier is None or not (1 <= second_multiplier <= 20):
                return redirect('multiplication_to_20', mode=1)

            # Сохраняем диапазоны и случайные числа в сессии
            request.session['first_multiplier_range'] = first_multiplier_range  # Диапазон первого множителя
            request.session['second_multiplier'] = second_multiplier  # Указанный второй множитель
            
            first = random.choice(first_multipliers)  # Случайное число из первого диапазона
            
            # Случайно выбираем знак для первого числа
            first_sign = random.choice([-1, 1])
            first *= first_sign
            
            # Случайно выбираем знак для второго числа
            second_sign = random.choice([-1, 1])
            second = second_multiplier * second_sign
            
            request.session['first'] = first
            request.session['second'] = second

            # Переход на следующий этап (отображение примера)
            return redirect('multiplication_to_20', mode=2)

    elif mode == 2:  # Этап отображения примера
        first = request.session.get('first')  # Получаем первое число из сессии
        second = request.session.get('second')  # Получаем второе число из сессии

        # Если чисел нет в сессии, возвращаем пользователя на этап выбора
        if first is None or second is None:
            return redirect('multiplication_to_20', mode=1)

        # Отображаем шаблон с примером для умножения
        return render(request, 'multiplication_to_20.html', {
            'first': first,
            'second': second,
            'operation': '×',  # Знак умножения
            'mode': 2
        })

    elif mode == 3:  # Этап проверки ответа
        first = request.session.get('first')  # Получаем первое число
        second = request.session.get('second')  # Получаем второе число
        first_multiplier_range = request.session.get('first_multiplier_range')  # Получаем диапазон первого числа
        second_multiplier = request.session.get('second_multiplier')  # Получаем второй множитель

        if request.method == 'POST':  # Если запрос POST
            user_answer = request.POST.get('user-answer')  # Получаем ответ пользователя
            correct_answer = first * second  # Вычисляем правильный ответ

            # Проверка правильности ответа
            if user_answer and user_answer.isdigit() and int(user_answer) == correct_answer:
                result_message = "Верно! Молодец!"  # Сообщение о правильном ответе
                result_color = "green"  # Цвет сообщения

                # Генерируем новый пример
                first_multipliers = RANGES.get(first_multiplier_range,
                                               [])  # Получаем список чисел для первого множителя

                if first_multipliers:
                    new_first = random.choice(first_multipliers)  # Случайное число для нового примера
                    
                    # Случайно выбираем знак для нового первого числа
                    first_sign = random.choice([-1, 1])
                    new_first *= first_sign
                    
                    # Случайно выбираем знак для второго числа
                    second_sign = random.choice([-1, 1])
                    new_second = second * second_sign
                    
                    request.session['first'] = new_first
                    request.session['second'] = new_second
            else:
                result_message = "Неверно! Попробуйте снова."  # Сообщение о неверном ответе
                result_color = "red"  # Цвет сообщения

            # Отображаем шаблон с результатом проверки
            return render(request, 'multiplication_to_20.html', {
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'result': result_message,
                'result_color': result_color,
                'mode': 3
            })

        # Если запрос GET, возвращаем пользователя на предыдущий этап (отображение примера)
        return redirect('multiplication_to_20', mode=2)


# Обработчик выбора и проверки возведения в квадрат
def square(request, mode):
    # Проверяем авторизацию ученика или учителя
    if not request.session.get('student_id') and not (hasattr(request.user, 'teacher_profile') and request.user.teacher_profile.status == 'approved'):
        return redirect('student_login')
    
    if mode == 1:
        if request.method == 'GET':
            return render(request, 'square.html', {"mode": 1})

        if request.method == 'POST':
            selected_ranges = request.POST.getlist('number-ranges')

            if not selected_ranges:
                return redirect('square', mode=1)

            # Генерируем список возможных чисел из выбранных диапазонов
            possible_numbers = []
            for r in selected_ranges:
                possible_numbers.extend(RANGES.get(r, []))

            if not possible_numbers:
                return redirect('square', mode=1)

            # Выбираем только одно случайное число
            selected_number = random.choice(possible_numbers)

            # Сохраняем число и настройки в сессии
            request.session['square_number'] = selected_number
            request.session['selected_ranges'] = selected_ranges

            # Пропускаем отсчет и сразу показываем число
            return redirect('square', mode=3)

    elif mode == 2:
        # Проверяем, есть ли параметр next_mode для перехода к режиму 3
        if request.method == 'POST' and request.POST.get('next_mode') == '3':
            return redirect('square', mode=3)

        # Отсчет перед началом игры
        return render(request, 'square.html', {"mode": 2})

    elif mode == 3:
        # Проверяем, есть ли параметр next_mode для перехода к режиму 4
        if request.method == 'POST' and request.POST.get('next_mode') == '4':
            return redirect('square', mode=4)

        # Показ числа для возведения в квадрат
        current_number = request.session.get('square_number')

        if current_number is None:
            return redirect('square', mode=1)
        
        return render(request, 'square.html', {
            'mode': 3,
            'number': current_number,
            'current_index': 1,
            'total_count': 1
        })

    elif mode == 4:
        # Ввод ответа
        current_number = request.session.get('square_number')

        if current_number is None:
            return redirect('square', mode=1)

        if request.method == 'POST':
            user_answer = request.POST.get('user_answer')
            correct_answer = current_number ** 2

            if user_answer and user_answer.isdigit() and int(user_answer) == correct_answer:
                is_correct = True
                result_message = "Верно! Молодец!"
            else:
                is_correct = False
                result_message = "Неверно! Попробуйте снова."

            # Сохраняем результат и переходим к показу результатов
            request.session['is_correct'] = is_correct
            request.session['user_answer'] = user_answer
            request.session['correct_answer'] = correct_answer
            request.session['result'] = result_message
            return redirect('square', mode=5)

        return render(request, 'square.html', {
            'mode': 4,
            'current_number': current_number
        })

    elif mode == 5:
        # Результаты игры
        return render(request, 'square.html', {
            'mode': 5,
            'is_correct': request.session.get('is_correct', False),
            'user_answer': request.session.get('user_answer', ''),
            'correct_answer': request.session.get('correct_answer', ''),
            'result': request.session.get('result', '')
        })


# Обработчик выбора и проверки умножение от базы
def multiplication_base(request, mode):
    # Проверяем авторизацию ученика или учителя
    if not request.session.get('student_id') and not (hasattr(request.user, 'teacher_profile') and request.user.teacher_profile.status == 'approved'):
        return redirect('student_login')
    
    if mode == 1:
        if request.method == 'GET':
            return render(request, 'multiplication_base.html', {"mode": 1})

        if request.method == 'POST':
            selected_ranges = request.POST.getlist('multiplier-range')

            first_multipliers = []
            for r in selected_ranges:
                first_multipliers.extend(RANGES.get(r, []))

            if not first_multipliers:
                return redirect('multiplication_base', mode=1)

            first = random.choice(first_multipliers)
            second = random.choice(first_multipliers)
            
            # Случайно выбираем знак для чисел
            first_sign = random.choice([-1, 1])
            second_sign = random.choice([-1, 1])
            
            first *= first_sign
            second *= second_sign

            request.session['first'] = first
            request.session['second'] = second
            request.session['selected_ranges'] = selected_ranges

            return redirect('multiplication_base', mode=2)

    elif mode == 2:
        first = request.session.get('first')
        second = request.session.get('second')

        if first is None or second is None:
            return redirect('multiplication_base', mode=1)

        return render(request, 'multiplication_base.html', {
            'first': first,
            'second': second,
            'operation': '×',
            'mode': 2
        })

    elif mode == 3:
        first = request.session.get('first')
        second = request.session.get('second')
        selected_ranges = request.session.get('selected_ranges', [])

        if request.method == 'POST':
            user_answer = request.POST.get('user-answer')
            correct_answer = first * second

            if user_answer and user_answer.isdigit() and int(user_answer) == correct_answer:
                result_message = "Верно! Молодец!"
                result_color = "green"

                first_multipliers = []
                for r in selected_ranges:
                    first_multipliers.extend(RANGES.get(r, []))

                if first_multipliers:
                    new_first = random.choice(first_multipliers)  # Случайное число для нового примера
                    new_second = random.choice(first_multipliers)  # Случайное число для нового примера
                    
                    # Случайно выбираем знак для новых чисел
                    first_sign = random.choice([-1, 1])
                    second_sign = random.choice([-1, 1])
                    
                    new_first *= first_sign
                    new_second *= second_sign
                    
                    request.session['first'] = new_first
                    request.session['second'] = new_second
            else:
                result_message = "Неверно! Попробуйте снова."
                result_color = "red"

            return render(request, 'multiplication_base.html', {
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'result': result_message,
                'result_color': result_color,
                'mode': 3
            })

        return redirect('multiplication_base', mode=2)


# функция для определения двух множителей при выборе двухзначных чисел
def generate_two_digit_pair():
    """Генерирует пару двузначных чисел с одинаковым десятком и суммой единиц 10."""
    tens = random.randint(1, 9)  # Выбираем десяток от 10 до 90
    unit1 = random.randint(1, 9)  # Выбираем первую единицу
    unit2 = 10 - unit1  # Вторая единица должна дополнять до 10
    first = tens * 10 + unit1
    second = tens * 10 + unit2
    
    # Случайно выбираем знак для чисел
    first_sign = random.choice([-1, 1])
    second_sign = random.choice([-1, 1])
    
    first *= first_sign
    second *= second_sign
    
    return first, second


# функция для определения двух множителей при выборе трехзначных чисел
def generate_three_digit_pair():
    """Генерирует пару трехзначных чисел с одинаковыми сотнями и десятками, сумма единиц 10."""
    hundreds = random.randint(1, 9)  # Выбираем сотню (100-900)
    tens = random.randint(0, 9)  # Выбираем десяток (00-90)
    unit1 = random.randint(1, 9)  # Выбираем первую единицу
    unit2 = 10 - unit1  # Вторая единица дополняет до 10
    first = hundreds * 100 + tens * 10 + unit1
    second = hundreds * 100 + tens * 10 + unit2
    
    # Случайно выбираем знак для чисел
    first_sign = random.choice([-1, 1])
    second_sign = random.choice([-1, 1])
    
    first *= first_sign
    second *= second_sign
    
    return first, second


# Обработчик выбора и проверки хитрости
def tricks(request, mode):
    # Проверяем авторизацию ученика или учителя
    if not request.session.get('student_id') and not (hasattr(request.user, 'teacher_profile') and request.user.teacher_profile.status == 'approved'):
        return redirect('student_login')
    
    if mode == 1:
        if request.method == 'GET':
            return render(request, 'tricks.html', {"mode": 1})

        if request.method == 'POST':
            number_type = request.POST.get('number-type')  # Двузначные или трехзначные

            if number_type == "2":  # Обрабатываем "2" как двузначные
                first, second = generate_two_digit_pair()
            elif number_type == "3":  # Обрабатываем "3" как трехзначные
                first, second = generate_three_digit_pair()
            else:
                return redirect('tricks', mode=1)  # В случае ошибки вернемся к выбору типа чисел

            # Сохраняем данные в сессии
            request.session['first'] = first
            request.session['second'] = second
            request.session['number_type'] = number_type

            return redirect('tricks', mode=2)  # Переход к режиму 2

    elif mode == 2:
        # Получаем данные из сессии
        first = request.session.get('first')
        second = request.session.get('second')

        if first is None or second is None:
            return redirect('tricks', mode=1)  # Если данных нет в сессии, возвращаем на выбор чисел

        return render(request, 'tricks.html', {
            'first': first,
            'second': second,
            'operation': '×',
            'mode': 2
        })

    elif mode == 3:
        first = request.session.get('first')
        second = request.session.get('second')
        number_type = request.session.get('number_type')

        if first is None or second is None:
            return redirect('tricks', mode=1)  # Если данных нет в сессии, возвращаем на выбор чисел

        if request.method == 'POST':
            user_answer = request.POST.get('user-answer')
            correct_answer = first * second

            if user_answer and user_answer.isdigit() and int(user_answer) == correct_answer:
                result_message = "Верно! Молодец!"
                result_color = "green"

                # Генерируем новую пару
                if number_type == "2":
                    first, second = generate_two_digit_pair()
                elif number_type == "3":
                    first, second = generate_three_digit_pair()

                # Сохраняем новую пару в сессии
                request.session['first'] = first
                request.session['second'] = second
            else:
                result_message = "Неверно! Попробуйте снова."
                result_color = "red"

            return render(request, 'tricks.html', {
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'result': result_message,
                'result_color': result_color,
                'mode': 3
            })

        return redirect('tricks', mode=2)  # Если не было отправлено ответа, возвращаем на режим 2


# Новые представления для учителей

def teacher_register(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # После успешной регистрации перенаправляем на страницу ожидания подтверждения
            return redirect('teacher_pending_approval')
    else:
        form = TeacherRegistrationForm()
    
    return render(request, 'teacher_register.html', {'form': form})

def teacher_pending_approval(request):
    """Страница ожидания подтверждения статуса учителя администратором"""
    return render(request, 'teacher_pending_approval.html')

def teacher_login(request):
    if request.method == 'POST':
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                try:
                    teacher_profile = user.teacher_profile
                    if teacher_profile.status == 'approved':
                        login(request, user)
                        return redirect('teacher_dashboard')
                    elif teacher_profile.status == 'pending':
                        messages.warning(request, 'Ваш аккаунт ожидает подтверждения администратором. Для ускорения процесса свяжитесь по номеру: +375291210908')
                    elif teacher_profile.status == 'rejected':
                        messages.error(request, 'Ваша заявка была отклонена. Обратитесь к администратору для выяснения причин.')
                    else:
                        messages.error(request, 'Неизвестный статус аккаунта. Обратитесь к администратору.')
                except TeacherProfile.DoesNotExist:
                    messages.error(request, 'Профиль учителя не найден. Обратитесь к администратору.')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = TeacherLoginForm()
    
    return render(request, 'teacher_login.html', {'form': form})

@login_required
def teacher_logout(request):
    logout(request)
    return redirect('index')

@login_required
def teacher_dashboard(request):
    try:
        teacher_profile = request.user.teacher_profile
        if teacher_profile.status != 'approved':
            return redirect('teacher_login')
        
        classes = Class.objects.filter(teacher=teacher_profile)
        total_students = Students.objects.filter(student_class__teacher=teacher_profile).count()
        
        context = {
            'teacher_profile': teacher_profile,
            'classes': classes,
            'total_students': total_students,
        }
        return render(request, 'teacher_dashboard.html', context)
    except TeacherProfile.DoesNotExist:
        return redirect('teacher_login')

@login_required
def class_list(request):
    try:
        teacher_profile = request.user.teacher_profile
        if teacher_profile.status != 'approved':
            return HttpResponseForbidden('Доступ запрещен')
        
        classes = Class.objects.filter(teacher=teacher_profile)
        return render(request, 'class_list.html', {'classes': classes})
    except TeacherProfile.DoesNotExist:
        return HttpResponseForbidden('Доступ запрещен')

@login_required
def class_create(request):
    try:
        teacher_profile = request.user.teacher_profile
        if teacher_profile.status != 'approved':
            return HttpResponseForbidden('Доступ запрещен')
        
        if request.method == 'POST':
            form = ClassForm(request.POST)
            if form.is_valid():
                class_obj = form.save(commit=False)
                class_obj.teacher = teacher_profile
                class_obj.save()
                messages.success(request, 'Класс успешно создан!')
                return redirect('class_list')
        else:
            form = ClassForm()
        
        return render(request, 'class_form.html', {'form': form, 'title': 'Создать класс'})
    except TeacherProfile.DoesNotExist:
        return HttpResponseForbidden('Доступ запрещен')

@login_required
def class_edit(request, class_id):
    try:
        teacher_profile = request.user.teacher_profile
        if teacher_profile.status != 'approved':
            return HttpResponseForbidden('Доступ запрещен')
        
        class_obj = get_object_or_404(Class, id=class_id, teacher=teacher_profile)
        
        if request.method == 'POST':
            form = ClassForm(request.POST, instance=class_obj)
            if form.is_valid():
                form.save()
                messages.success(request, 'Класс успешно обновлен!')
                return redirect('class_list')
        else:
            form = ClassForm(instance=class_obj)
        
        return render(request, 'class_form.html', {'form': form, 'title': 'Редактировать класс', 'class_obj': class_obj})
    except TeacherProfile.DoesNotExist:
        return HttpResponseForbidden('Доступ запрещен')

@login_required
def class_delete(request, class_id):
    try:
        teacher_profile = request.user.teacher_profile
        if teacher_profile.status != 'approved':
            return HttpResponseForbidden('Доступ запрещен')
        
        class_obj = get_object_or_404(Class, id=class_id, teacher=teacher_profile)
        class_obj.delete()
        messages.success(request, 'Класс успешно удален!')
        return redirect('class_list')
    except TeacherProfile.DoesNotExist:
        return HttpResponseForbidden('Доступ запрещен')

@login_required
def students_list(request, class_id=None):
    try:
        teacher_profile = request.user.teacher_profile
        if teacher_profile.status != 'approved':
            return HttpResponseForbidden('Доступ запрещен')
        
        if class_id:
            class_obj = get_object_or_404(Class, id=class_id, teacher=teacher_profile)
            students = Students.objects.filter(student_class=class_obj).order_by('surname', 'name')
            context = {'students': students, 'class_obj': class_obj}
        else:
            students = Students.objects.filter(student_class__teacher=teacher_profile).order_by('surname', 'name')
            context = {'students': students}
        
        return render(request, 'students_list.html', context)
    except TeacherProfile.DoesNotExist:
        return HttpResponseForbidden('Доступ запрещен')

@login_required
def student_create(request, class_id=None):
    logger.debug(f"student_create called with class_id: {class_id}")
    try:
        teacher_profile = request.user.teacher_profile
        logger.debug(f"Teacher profile: {teacher_profile}")
        if teacher_profile.status != 'approved':
            logger.warning(f"Teacher {request.user.username} not approved, status: {teacher_profile.status}")
            return HttpResponseForbidden('Доступ запрещен')
        
        if request.method == 'POST':
            logger.debug("Processing POST request for student creation")
            form = StudentForm(request.POST)
            logger.debug(f"Form data: {request.POST}")
            if form.is_valid():
                logger.debug("Form is valid, creating student")
                student = form.save(commit=False)
                if class_id:
                    student.student_class = get_object_or_404(Class, id=class_id, teacher=teacher_profile)
                else:
                    # Если класс не указан, предлагаем выбрать из списка классов учителя
                    classes = Class.objects.filter(teacher=teacher_profile)
                    if classes.count() == 1:
                        student.student_class = classes.first()
                    else:
                        # Получаем выбранный класс из формы
                        selected_class_id = request.POST.get('student_class')
                        if selected_class_id:
                            student.student_class = get_object_or_404(Class, id=selected_class_id, teacher=teacher_profile)
                        else:
                            # Если класс не выбран, показываем форму с выбором класса
                            return render(request, 'student_form.html', {
                                'form': form, 
                                'title': 'Добавить ученика',
                                'classes': classes,
                                'need_class_selection': True
                            })
                
                logger.debug(f"Saving student: {student}")
                student.save()
                logger.info(f"Student {student.surname} {student.name} successfully created")
                messages.success(request, 'Ученик успешно добавлен!')
                
                # Если ученик добавлен в класс, предлагаем создать расписание
                if class_id:
                    # Проверяем, есть ли уже ученики в классе
                    students_count = Students.objects.filter(student_class=student.student_class).count()
                    if students_count > 0:
                        messages.info(request, f'Теперь в классе "{student.student_class.name}" есть ученики. Вы можете создать месячное расписание.')
                        return redirect('monthly_schedule_create', class_id=class_id)
                    else:
                        return redirect('students_list_by_class', class_id=class_id)
                else:
                    return redirect('students_list')
        else:
            form = StudentForm()
        
        context = {
            'form': form, 
            'title': 'Добавить ученика',
            'class_id': class_id
        }
        
        if class_id:
            context['class_obj'] = get_object_or_404(Class, id=class_id, teacher=teacher_profile)
            # Проверяем, есть ли ученики в классе
            students_count = Students.objects.filter(student_class=context['class_obj']).count()
            if students_count == 0:
                context['show_schedule_info'] = True
                context['schedule_message'] = f'В классе "{context["class_obj"].name}" нет учеников. После добавления ученика вы сможете создать месячное расписание.'
        
        return render(request, 'student_form.html', context)
    except TeacherProfile.DoesNotExist:
        logger.error(f"TeacherProfile not found for user {request.user.username}")
        return HttpResponseForbidden('Доступ запрещен')
    except Exception as e:
        logger.error(f"Unexpected error in student_create: {str(e)}", exc_info=True)
        messages.error(request, 'Произошла ошибка при создании ученика')
        return render(request, 'student_form.html', {
            'form': form if 'form' in locals() else StudentForm(),
            'title': 'Добавить ученика',
            'class_id': class_id,
            'error': str(e)
        })

@login_required
def student_edit(request, student_id):
    try:
        teacher_profile = request.user.teacher_profile
        if teacher_profile.status != 'approved':
            return HttpResponseForbidden('Доступ запрещен')
        
        student = get_object_or_404(Students, id=student_id, student_class__teacher=teacher_profile)
        
        if request.method == 'POST':
            form = StudentForm(request.POST, instance=student)
            if form.is_valid():
                form.save()
                messages.success(request, 'Данные ученика успешно обновлены!')
                return redirect('students_list')
        else:
            form = StudentForm(instance=student)
        
        return render(request, 'student_form.html', {
            'form': form, 
            'title': 'Редактировать ученика',
            'student': student
        })
    except TeacherProfile.DoesNotExist:
        return HttpResponseForbidden('Доступ запрещен')

@login_required
def student_delete(request, student_id):
    try:
        teacher_profile = request.user.teacher_profile
        if teacher_profile.status != 'approved':
            return HttpResponseForbidden('Доступ запрещен')
        
        student = get_object_or_404(Students, id=student_id, student_class__teacher=teacher_profile)
        student.delete()
        messages.success(request, 'Ученик успешно удален!')
        return redirect('students_list')
    except TeacherProfile.DoesNotExist:
        return HttpResponseForbidden('Доступ запрещен')

@login_required
def teacher_profile_edit(request):
    try:
        teacher_profile = request.user.teacher_profile
        if request.method == 'POST':
            form = TeacherProfileUpdateForm(request.POST, instance=teacher_profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Профиль успешно обновлен!')
                return redirect('teacher_dashboard')
        else:
            form = TeacherProfileUpdateForm(instance=teacher_profile)
        
        return render(request, 'teacher_profile_edit.html', {'form': form})
    except TeacherProfile.DoesNotExist:
        messages.error(request, 'У вас нет профиля учителя.')
        return redirect('teacher_login')


# Обработчик выбора и проверки игры "Просто"

# Определяем диапазоны для игры "Просто"
SIMPLY_RANGES = {
    "1-10": (1, 10),
    "10-100": (10, 100),
    "100-1000": (100, 1000),
    "1000-10000": (1000, 10000),
}

def simply(request, mode):
    # Игра "просто" доступна всем пользователям без авторизации
    
    if mode == 1:
        if request.method == 'POST':
            range_key = request.POST.get('range')
            num_examples = request.POST.get('examples')
            speed = request.POST.get('speed')
            max_digit = request.POST.get('max_digit')
            
            # Очищаем только игровые данные из сессии, сохраняя аутентификацию
            game_keys = ['range_key', 'num_examples', 'speed', 'max_digit', 'game_numbers', 'game_total', 'current_number_index', 'user_answer', 'is_correct', 'correct_answer', 'current_sign']
            for key in game_keys:
                if key in request.session:
                    del request.session[key]
            
            # Сохраняем настройки в сессию
            request.session['range_key'] = int(range_key) if range_key else 2
            request.session['num_examples'] = int(num_examples) if num_examples else 10
            request.session['speed'] = float(speed) if speed else 1.0
            request.session['max_digit'] = int(max_digit) if max_digit else 9
            
            # Сохраняем настройки в базу данных для долгосрочного хранения (только для авторизованных пользователей)
            try:
                if request.user.is_authenticated:
                    settings_data = {
                        'range_key': int(range_key) if range_key else 2,
                        'num_examples': int(num_examples) if num_examples else 10,
                        'speed': float(speed) if speed else 1.0,
                        'max_digit': int(max_digit) if max_digit else 9
                    }
                    
                    game_settings, created = GameSettings.objects.get_or_create(
                        user=request.user,
                        game_type='simply',
                        defaults={'settings_data': settings_data}
                    )
                    
                    if not created:
                        # Обновляем существующие настройки
                        game_settings.settings_data = settings_data
                        game_settings.save()
            except Exception as e:
                pass
            
            return redirect('simply', mode=2)
        else:
            # Сначала пытаемся загрузить настройки из базы данных
            saved_settings = {
                'range_key': 2,
                'num_examples': 10,
                'speed': 1.0,
                'max_digit': 9
            }
            
            try:
                if request.user.is_authenticated:
                    # Пытаемся загрузить из базы данных для авторизованных пользователей
                    game_settings = GameSettings.objects.filter(
                        user=request.user,
                        game_type='simply'
                    ).first()
                    
                    if game_settings and game_settings.settings_data:
                        saved_settings.update(game_settings.settings_data)
            except Exception as e:
                pass
            
            # Если в БД нет настроек, пытаемся загрузить из сессии
            if saved_settings['range_key'] == 2 and saved_settings['num_examples'] == 10 and saved_settings['speed'] == 1.0 and saved_settings['max_digit'] == 9:
                session_settings = {
                    'range_key': request.session.get('range_key'),
                    'num_examples': request.session.get('num_examples'),
                    'speed': request.session.get('speed'),
                    'max_digit': request.session.get('max_digit')
                }
                
                # Обновляем только те значения, которые есть в сессии
                for key, value in session_settings.items():
                    if value is not None:
                        saved_settings[key] = value
            
            return render(request, 'simply.html', {
                "mode": 1,
                "saved_settings": saved_settings
            })
    
    elif mode == 2:
        if request.method == 'POST':
            next_mode = request.POST.get('next_mode')
            if next_mode == '3':
                # Переходим к генерации чисел
                return redirect('simply', mode=3)
        return render(request, 'simply.html', {"mode": 2})
    
    elif mode == 3:
        # Получаем настройки из сессии
        range_key = request.session.get('range_key', 2)
        num_examples = request.session.get('num_examples', 10)
        speed = request.session.get('speed', 1.0)
        max_digit = request.session.get('max_digit', 9)
        
        # Определяем диапазон чисел и максимальную сумму
        if range_key == 1:  # 1-10 (однозначные)
            min_num, max_num = 1, 10
            max_sum = max_digit  # Для однозначных: от 0 до max_digit
        elif range_key == 2:  # 10-100 (двузначные)
            min_num, max_num = 10, 100
            max_sum = max_digit * 11  # Для двузначных: от 0 до max_digit*11 (например, для 3: 0-33)
        elif range_key == 3:  # 100-1000 (трехзначные)
            min_num, max_num = 100, 1000
            max_sum = max_digit * 111  # Для трехзначных: от 0 до max_digit*111 (например, для 3: 0-333)
        elif range_key == 4:  # 1000-10000 (четырехзначные)
            min_num, max_num = 1000, 10000
            max_sum = max_digit * 1111  # Для четырехзначных: от 0 до max_digit*1111
        else:
            min_num, max_num = 10, 100
            max_sum = max_digit * 11
        
        # Генерируем числа, состоящие только из указанных цифр
        numbers = []
        available_digits = list(range(1, max_digit + 1))  # Цифры от 1 до max_digit
        
        # Определяем количество разрядов для чисел
        if range_key == 1:  # 1-10
            num_digits = 1
        elif range_key == 2:  # 10-100
            num_digits = 2
        elif range_key == 3:  # 100-1000
            num_digits = 3
        elif range_key == 4:  # 1000-10000
            num_digits = 4
        else:
            num_digits = 2
        
        # Генерируем целевую сумму в пределах от 0 до max_sum
        target_sum = random.randint(0, max_sum)
        
        # Начинаем генерацию чисел с учетом целевой суммы
        current_sum = 0
        attempts = 0
        max_attempts = 1000  # Ограничиваем количество попыток
        
        for i in range(num_examples):
            attempts = 0
            while attempts < max_attempts:
                attempts += 1
                
                # Генерируем число по разрядам
                number = 0
                for digit_pos in range(num_digits):
                    # Выбираем случайную цифру из доступных
                    digit = random.choice(available_digits)
                    # Добавляем цифру в соответствующий разряд
                    number += digit * (10 ** (num_digits - 1 - digit_pos))
                
                # Проверяем, что число попадает в нужный диапазон
                if not (min_num <= number <= max_num):
                    continue
                
                # Определяем возможные знаки для числа
                remaining_numbers = num_examples - i - 1
                
                if i == num_examples - 1:  # Последнее число
                    # Последнее число должно точно дать нужную сумму
                    needed_value = target_sum - current_sum
                    if abs(needed_value) == number:
                        sign = 1 if needed_value > 0 else -1
                        # Проверяем, что промежуточная сумма не уйдет в минус или не превысит max_sum
                        temp_sum = current_sum + (number * sign)
                        if 0 <= temp_sum <= max_sum:
                            final_number = number * sign
                            numbers.append(final_number)
                            current_sum += final_number
                            break
                    continue
                else:
                    # Для промежуточных чисел выбираем знак так, чтобы промежуточная сумма оставалась в пределах [0, max_sum]
                    possible_signs = []
                    
                    # Проверяем положительный знак
                    temp_sum_pos = current_sum + number
                    if 0 <= temp_sum_pos <= max_sum:
                        # Проверяем, что с оставшимися числами можно достичь целевой суммы
                        remaining_range = remaining_numbers * max_num
                        if temp_sum_pos - remaining_range <= target_sum <= temp_sum_pos + remaining_range:
                            possible_signs.append(1)
                    
                    # Проверяем отрицательный знак
                    temp_sum_neg = current_sum - number
                    if 0 <= temp_sum_neg <= max_sum:
                        # Проверяем, что с оставшимися числами можно достичь целевой суммы
                        remaining_range = remaining_numbers * max_num
                        if temp_sum_neg - remaining_range <= target_sum <= temp_sum_neg + remaining_range:
                            possible_signs.append(-1)
                    
                    if possible_signs:
                        sign = random.choice(possible_signs)
                        final_number = number * sign
                        numbers.append(final_number)
                        current_sum += final_number
                        break
            
            # Если не удалось найти подходящее число за разумное количество попыток
            if attempts >= max_attempts:
                # Перезапускаем генерацию с новой целевой суммой
                numbers = []
                current_sum = 0
                target_sum = random.randint(0, max_sum)
                i = -1  # Начинаем заново
                continue
        
        # Если что-то пошло не так, используем простую генерацию
        if len(numbers) != num_examples:
            numbers = []
            current_sum = 0
            
            for i in range(num_examples):
                # Генерируем простое число
                number = 0
                for digit_pos in range(num_digits):
                    digit = random.choice(available_digits)
                    number += digit * (10 ** (num_digits - 1 - digit_pos))
                
                # Ограничиваем число диапазоном
                number = max(min_num, min(number, max_num))
                
                # Определяем знак так, чтобы промежуточная сумма оставалась в пределах [0, max_sum]
                possible_signs = []
                
                # Проверяем положительный знак
                if current_sum + number <= max_sum:
                    possible_signs.append(1)
                
                # Проверяем отрицательный знак (только если промежуточная сумма не уйдет в минус)
                if current_sum - number >= 0:
                    possible_signs.append(-1)
                
                # Если нет подходящих знаков, используем положительный
                if not possible_signs:
                    sign = 1
                    # Корректируем число, чтобы не превысить max_sum
                    if current_sum + number > max_sum:
                        number = max_sum - current_sum
                        if number < min_num:
                            number = min_num
                else:
                    sign = random.choice(possible_signs)
                
                final_number = number * sign
                numbers.append(final_number)
                current_sum += final_number
                
                # Дополнительная проверка: если сумма все еще выходит за пределы, корректируем
                if current_sum < 0:
                    current_sum = 0
                elif current_sum > max_sum:
                    current_sum = max_sum
        
        # Вычисляем итоговую сумму
        game_total = sum(numbers)
        
        # Убеждаемся, что сумма в допустимых пределах
        if game_total < 0:
            game_total = 0
        elif game_total > max_sum:
            game_total = max_sum
        
        # Сохраняем данные в сессию
        request.session['game_numbers'] = numbers
        request.session['game_total'] = game_total
        request.session['current_number_index'] = 0
        request.session['speed'] = speed
        
        return redirect('simply', mode=5)
    
    elif mode == 5:
        if request.method == 'POST':
            next_mode = request.POST.get('next_mode')
            if next_mode == '6':
                # Переходим к вводу ответа
                return redirect('simply', mode=6)
            elif next_mode == '7':
                # Переходим к следующему числу
                return redirect('simply', mode=7)
        
        # Получаем данные из сессии
        numbers = request.session.get('game_numbers', [])
        current_index = request.session.get('current_number_index', 0)
        speed = request.session.get('speed', 1.0)
        
        if not numbers:
            return redirect('simply', mode=1)
        
        if current_index >= len(numbers):
            return redirect('simply', mode=6)
        
        current_number = numbers[current_index]
        
        context = {
            "mode": 5,
            "current_number": current_number,
            "current_index": current_index + 1,  # +1 для отображения (начиная с 1)
            "total_count": len(numbers),
            "speed": speed
        }
        
        return render(request, 'simply.html', context)
    
    elif mode == 6:
        if request.method == 'POST':
            user_answer = request.POST.get('user_answer')
            game_total = request.session.get('game_total', 0)
            
            try:
                user_answer = int(user_answer)
                is_correct = user_answer == game_total
                
                # Сохраняем результат
                request.session['user_answer'] = user_answer
                request.session['is_correct'] = is_correct
                request.session['correct_answer'] = game_total
                
                return redirect('simply', mode=4)
                
            except (ValueError, TypeError):
                return redirect('simply', mode=6)
        else:
            return render(request, 'simply.html', {"mode": 6})
    
    elif mode == 7:
        # Увеличиваем индекс
        current_index = request.session.get('current_number_index', 0)
        new_index = current_index + 1
        
        request.session['current_number_index'] = new_index
        
        # Проверяем, показаны ли все числа
        numbers = request.session.get('game_numbers', [])
        if new_index >= len(numbers):
            return redirect('simply', mode=6)
        else:
            return redirect('simply', mode=5)
    
    elif mode == 4:
        # Получаем результаты из сессии
        user_answer = request.session.get('user_answer', 0)
        is_correct = request.session.get('is_correct', False)
        correct_answer = request.session.get('correct_answer', 0)
        game_numbers = request.session.get('game_numbers', [])
        
        context = {
            "mode": 4,
            "user_answer": user_answer,
            "is_correct": is_correct,
            "correct_answer": correct_answer,
            "game_numbers": game_numbers
        }
        
        return render(request, 'simply.html', context)
    
    else:
        return redirect('simply', mode=1)

# Представления для учеников

def student_login(request):
    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            try:
                student_account = StudentAccount.objects.get(username=username, is_active=True)
                if student_account.password == password:  # Простая проверка пароля
                    # Обновляем время последнего входа
                    student_account.last_login = timezone.now()
                    student_account.save()
                    
                    # Сохраняем информацию об ученике в сессии
                    request.session['student_id'] = student_account.student.id
                    request.session['student_name'] = f"{student_account.student.surname} {student_account.student.name}"
                    
                    return redirect('student_dashboard')
                else:
                    return redirect('student_login')
            except StudentAccount.DoesNotExist:
                return redirect('student_login')
    else:
        form = StudentLoginForm()
    
    return render(request, 'student_login.html', {'form': form})

def student_logout(request):
    if 'student_id' in request.session:
        del request.session['student_id']
        del request.session['student_name']
    return redirect('index')

def student_dashboard(request):
    if 'student_id' not in request.session:
        return redirect('student_login')
    
    student_id = request.session['student_id']
    student = get_object_or_404(Students, id=student_id)
    
    # Получаем доступные игры для класса ученика
    available_games = []
    if student.student_class:
        # Получаем все игры, доступные для класса
        class_games = ClassGameAccess.objects.filter(
            class_group=student.student_class,
            is_enabled=True
        )
        
        # Добавляем отладочную информацию
        print(f"DEBUG: Ученик {student.name} в классе {student.student_class.name}")
        print(f"DEBUG: Найдено {class_games.count()} доступных игр")
        
        # Показываем все найденные игры
        for game in class_games:
            print(f"DEBUG: В БД найдена игра: {game.game} -> {game.is_enabled}")
        
        # Создаем список доступных игр
        for game_access in class_games:
            print(f"DEBUG: Игра {game_access.game} доступна")
            if game_access.game == 'multiplication_choose':
                available_games.append({
                    'code': 'multiplication_choose',
                    'title': 'Умножение',
                    'description': 'Изучайте таблицу умножения с разными диапазонами чисел.',
                    'icon': 'fas fa-times',
                    'url': 'multiplication_choose'
                })
            elif game_access.game == 'multiplication_to_20':
                available_games.append({
                    'code': 'multiplication_to_20',
                    'title': 'Умножение до 20',
                    'description': 'Специальная тренировка умножения чисел до 20.',
                    'icon': 'fas fa-calculator',
                    'url': 'multiplication_to_20'
                })
            elif game_access.game == 'square':
                available_games.append({
                    'code': 'square',
                    'title': 'Квадрат',
                    'description': 'Тренируйте возведение чисел в квадрат и умножение.',
                    'icon': 'fas fa-square',
                    'url': 'square'
                })
            elif game_access.game == 'multiplication_base':
                available_games.append({
                    'code': 'multiplication_base',
                    'title': 'Умножение от базы',
                    'description': 'Специальные техники умножения с использованием базовых чисел.',
                    'icon': 'fas fa-sort-numeric-up',
                    'url': 'multiplication_base'
                })
            elif game_access.game == 'tricks':
                available_games.append({
                    'code': 'tricks',
                    'title': 'Хитрости',
                    'description': 'Изучайте специальные математические хитрости для быстрого счета.',
                    'icon': 'fas fa-magic',
                    'url': 'tricks'
                })
            elif game_access.game == 'flashcards':
                available_games.append({
                    'code': 'flashcards',
                    'title': 'Флэшкарты',
                    'description': 'Тренируйте ментальную арифметику с помощью счетов (абакуса).',
                    'icon': 'fas fa-credit-card',
                    'url': 'flashcards'
                })
            else:
                print(f"DEBUG: Неизвестная игра: {game_access.game}")
    
    print(f"DEBUG: Итого доступно игр: {len(available_games)}")
    
    # Игра "Просто" всегда доступна
    available_games.insert(0, {
        'code': 'simply',
        'title': 'Просто',
        'description': 'Тренируйте сложение и вычитание чисел. Выберите сложность и количество примеров.',
        'icon': 'fas fa-plus',
        'url': 'simply'
    })
    
    context = {
        'student': student,
        'student_name': request.session.get('student_name', ''),
        'available_games': available_games
    }
    return render(request, 'student_dashboard.html', context)

@login_required
def create_student_account(request, student_id):
    try:
        teacher_profile = request.user.teacher_profile
        if teacher_profile.status != 'approved':
            return HttpResponseForbidden('Доступ запрещен')
        
        student = get_object_or_404(Students, id=student_id, student_class__teacher=teacher_profile)
        
        # Проверяем, есть ли уже аккаунт у ученика
        if hasattr(student, 'account'):
            messages.warning(request, f'У ученика {student.name} уже есть аккаунт.')
            return redirect('students_list')
        
        if request.method == 'POST':
            form = StudentAccountForm(request.POST)
            if form.is_valid():
                account = form.save(commit=False)
                account.student = student
                account.save()
                messages.success(request, f'Аккаунт для ученика {student.name} успешно создан!')
                return redirect('students_list')
        else:
            form = StudentAccountForm()
        
        return render(request, 'create_student_account.html', {
            'form': form,
            'student': student,
            'title': 'Создать аккаунт для ученика'
        })
    except TeacherProfile.DoesNotExist:
        return HttpResponseForbidden('Доступ запрещен')

@login_required
def delete_student_account(request, student_id):
    try:
        teacher_profile = request.user.teacher_profile
        if teacher_profile.status != 'approved':
            return HttpResponseForbidden('Доступ запрещен')
        
        student = get_object_or_404(Students, id=student_id, student_class__teacher=teacher_profile)
        
        if hasattr(student, 'account'):
            student.account.delete()
            messages.success(request, f'Аккаунт ученика {student.name} успешно удален!')
        else:
            messages.warning(request, f'У ученика {student.name} нет аккаунта.')
        
        return redirect('students_list')
    except TeacherProfile.DoesNotExist:
        return HttpResponseForbidden('Доступ запрещен')

# Представления для домашних заданий
@login_required
def homework_list(request, class_id):
    """Список домашних заданий для класса"""
    try:
        class_obj = Class.objects.get(id=class_id)
        # Проверяем, что учитель имеет доступ к этому классу
        if class_obj.teacher != request.user.teacher_profile:
            return HttpResponseForbidden("У вас нет доступа к этому классу")
        
        homeworks = Homework.objects.filter(class_group=class_obj, is_active=True)
        return render(request, 'homework_list.html', {
            'class_obj': class_obj,
            'homeworks': homeworks
        })
    except Class.DoesNotExist:
        messages.error(request, 'Класс не найден')
        return redirect('class_list')

@login_required
def homework_create(request, class_id):
    """Создание нового домашнего задания"""
    try:
        class_obj = Class.objects.get(id=class_id)
        # Проверяем, что учитель имеет доступ к этому классу
        if class_obj.teacher != request.user.teacher_profile:
            return HttpResponseForbidden("У вас нет доступа к этому классу")
        
        if request.method == 'POST':
            form = HomeworkForm(request.POST)
            if form.is_valid():
                homework = form.save(commit=False)
                homework.class_group = class_obj
                homework.save()
                messages.success(request, 'Домашнее задание успешно создано!')
                return redirect('homework_list', class_id=class_id)
        else:
            form = HomeworkForm()
        
        return render(request, 'homework_form.html', {
            'form': form,
            'class_obj': class_obj,
            'title': 'Создать домашнее задание'
        })
    except Class.DoesNotExist:
        messages.error(request, 'Класс не найден')
        return redirect('class_list')

@login_required
def homework_edit(request, homework_id):
    """Редактирование домашнего задания"""
    try:
        homework = Homework.objects.get(id=homework_id)
        # Проверяем, что учитель имеет доступ к этому классу
        if homework.class_group.teacher != request.user.teacher_profile:
            return HttpResponseForbidden("У вас нет доступа к этому заданию")
        
        if request.method == 'POST':
            form = HomeworkForm(request.POST, instance=homework)
            if form.is_valid():
                form.save()
                messages.success(request, 'Домашнее задание успешно обновлено!')
                return redirect('homework_list', class_id=homework.class_group.id)
        else:
            form = HomeworkForm(instance=homework)
        
        return render(request, 'homework_form.html', {
            'form': form,
            'homework': homework,
            'class_obj': homework.class_group,
            'title': 'Редактировать домашнее задание'
        })
    except Homework.DoesNotExist:
        messages.error(request, 'Домашнее задание не найдено')
        return redirect('class_list')

@login_required
def homework_delete(request, homework_id):
    """Удаление домашнего задания"""
    try:
        homework = Homework.objects.get(id=homework_id)
        # Проверяем, что учитель имеет доступ к этому классу
        if homework.class_group.teacher != request.user.teacher_profile:
            return HttpResponseForbidden("У вас нет доступа к этому заданию")
        
        class_id = homework.class_group.id
        homework.delete()
        messages.success(request, 'Домашнее задание успешно удалено!')
        return redirect('homework_list', class_id=class_id)
    except Homework.DoesNotExist:
        messages.error(request, 'Домашнее задание не найдено')
        return redirect('class_list')

def student_homework_list(request):
    """Список домашних заданий для ученика"""
    if 'student_id' not in request.session:
        return redirect('student_login')
    
    try:
        student = Students.objects.get(id=request.session['student_id'])
        # Получаем класс ученика
        if hasattr(student, 'student_class') and student.student_class:
            homeworks = Homework.objects.filter(
                class_group=student.student_class, 
                is_active=True
            ).order_by('-created_at')
        else:
            homeworks = []
        
        return render(request, 'student_homework_list.html', {
            'student': student,
            'homeworks': homeworks,
            'today': timezone.now().date()
        })
    except Students.DoesNotExist:
        return redirect('student_login')


# Представления для табеля посещений

@login_required
def attendance_list(request, class_id):
    """Список посещений и оплат для класса"""
    class_obj = get_object_or_404(Class, id=class_id)
    
    # Проверяем, что пользователь является учителем этого класса
    if not hasattr(request.user, 'teacher_profile') or request.user.teacher_profile != class_obj.teacher:
        return HttpResponseForbidden("У вас нет доступа к этому классу")
    
    # Получаем всех учеников класса
    students = Students.objects.filter(student_class=class_obj).order_by('surname', 'name')
    
    # Получаем все даты занятий для этого класса
    attendance_dates = Attendance.objects.filter(
        class_group=class_obj
    ).values_list('date', flat=True).distinct().order_by('date')
    
    # Получаем данные о посещениях и оплатах
    attendance_data = {}
    for student in students:
        student_attendances = {}
        for date in attendance_dates:
            attendance = Attendance.objects.filter(
                class_group=class_obj,
                student=student,
                date=date
            ).first()
            
            if attendance:
                student_attendances[date] = {
                    'is_present': attendance.is_present,
                    'is_paid': attendance.is_paid
                }
        
        attendance_data[student.id] = {
            'attendances': student_attendances
        }
    
    context = {
        'class_obj': class_obj,
        'students': students,
        'attendance_dates': attendance_dates,
        'attendance_data': attendance_data,
    }
    
    return render(request, 'attendance_list.html', context)

@login_required
def attendance_create(request, class_id):
    """Создание одного занятия для класса"""
    class_obj = get_object_or_404(Class, id=class_id)
    
    # Проверяем, что пользователь является учителем этого класса
    if not hasattr(request.user, 'teacher_profile') or request.user.teacher_profile != class_obj.teacher:
        return HttpResponseForbidden("У вас нет доступа к этому классу")
    
    if request.method == 'POST':
        creation_type = request.POST.get('creation_type')
        
        if creation_type == 'single':
            new_date_str = request.POST.get('new_date')
            
            if not new_date_str:
                messages.error(request, 'Пожалуйста, выберите дату для занятия')
                return render(request, 'attendance_create.html', {'class_obj': class_obj})
            
            try:
                new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Неверный формат даты')
                return render(request, 'attendance_create.html', {'class_obj': class_obj})
            
            # Проверяем, не существует ли уже запись для этой даты
            existing_attendance = Attendance.objects.filter(
                class_group=class_obj,
                date=new_date
            ).first()
            
            if existing_attendance:
                messages.error(request, f'Занятие на {new_date.strftime("%d.%m.%Y")} уже существует')
                return render(request, 'attendance_create.html', {'class_obj': class_obj})
            
            # Получаем всех учеников класса
            students = Students.objects.filter(student_class=class_obj)
            
            # Создаем записи посещения для всех учеников
            attendance_records = []
            for student in students:
                attendance = Attendance.objects.create(
                    student=student,
                    class_group=class_obj,
                    date=new_date,
                    is_present=False,
                    is_paid=False
                )
                attendance_records.append(attendance)
            
            messages.success(request, f'Успешно создано занятие на {new_date.strftime("%d.%m.%Y")} для {len(attendance_records)} учеников')
            return redirect('attendance_list', class_id=class_id)
    
    return render(request, 'attendance_create.html', {'class_obj': class_obj})


@login_required
def attendance_add_date(request, class_id):
    """Добавление отдельного занятия для класса"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    try:
        class_obj = Class.objects.get(id=class_id)
        # Проверяем, что учитель имеет доступ к этому классу
        if class_obj.teacher != request.user.teacher_profile:
            return JsonResponse({'success': False, 'error': 'У вас нет доступа к этому классу'})
        
        new_date = request.POST.get('new_date')
        if not new_date:
            return JsonResponse({'success': False, 'error': 'Дата не указана'})
        
        try:
            new_date = timezone.datetime.strptime(new_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Неверный формат даты'})
        
        # Убираем ограничения по учебному году - позволяем добавлять занятия на любую дату
        
        # Проверяем, не существует ли уже записи для этой даты
        if Attendance.objects.filter(class_group=class_obj, date=new_date).exists():
            return JsonResponse({'success': False, 'error': 'Занятие на эту дату уже существует'})
        
        # Получаем всех учеников класса
        students = Students.objects.filter(student_class=class_obj)
        
        if not students.exists():
            return JsonResponse({'success': False, 'error': 'В классе нет учеников'})
        
        # Создаем записи посещения для всех учеников
        for student in students:
            Attendance.objects.create(
                student=student,
                class_group=class_obj,
                date=new_date,
                is_present=False,  # По умолчанию не присутствовал
                is_paid=False
            )
        
        return JsonResponse({'success': True, 'message': f'Занятие на {new_date.strftime("%d.%m.%Y")} успешно добавлено'})
        
    except Class.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Класс не найден'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Произошла ошибка: {str(e)}'})


@login_required
def attendance_delete_date(request, class_id):
    """Удаление отдельного занятия для класса"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    try:
        class_obj = Class.objects.get(id=class_id)
        # Проверяем, что учитель имеет доступ к этому классу
        if class_obj.teacher != request.user.teacher_profile:
            return JsonResponse({'success': False, 'error': 'У вас нет доступа к этому классу'})
        
        import json
        data = json.loads(request.body)
        date_to_delete = data.get('date')
        
        if not date_to_delete:
            return JsonResponse({'success': False, 'error': 'Дата не указана'})
        
        try:
            date_to_delete = timezone.datetime.strptime(date_to_delete, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Неверный формат даты'})
        
        # Удаляем все записи посещения для этой даты
        deleted_count = Attendance.objects.filter(
            class_group=class_obj, 
            date=date_to_delete
        ).delete()[0]
        
        if deleted_count > 0:
            return JsonResponse({'success': True, 'message': f'Занятие на {date_to_delete.strftime("%d.%m.%Y")} успешно удалено'})
        else:
            return JsonResponse({'success': False, 'error': 'Занятие на указанную дату не найдено'})
        
    except Class.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Класс не найден'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Произошла ошибка: {str(e)}'})


@login_required
def attendance_edit(request, class_id, date):
    """Редактирование посещений для определенной даты"""
    try:
        class_obj = Class.objects.get(id=class_id)
        # Проверяем, что учитель имеет доступ к этому классу
        if class_obj.teacher != request.user.teacher_profile:
            return HttpResponseForbidden("У вас нет доступа к этому классу")
        
        # Получаем все записи посещения для этой даты
        attendances = Attendance.objects.filter(
            class_group=class_obj,
            date=date
        ).select_related('student').order_by('student__surname', 'student__name')
        
        if request.method == 'POST':
            forms_valid = True
            updated_attendances = []
            
            # Сначала проверяем все формы
            for attendance in attendances:
                form = AttendanceForm(request.POST, instance=attendance, prefix=f'attendance_{attendance.id}')
                if not form.is_valid():
                    forms_valid = False
                    break
                updated_attendances.append((attendance, form))
            
            if forms_valid:
                # Сохраняем все формы
                for attendance, form in updated_attendances:
                    # Получаем данные из формы
                    is_present = form.cleaned_data.get('is_present', False)
                    is_paid = form.cleaned_data.get('is_paid', False)
                    notes = form.cleaned_data.get('notes', '')
                    
                    # Обновляем объект напрямую
                    attendance.is_present = is_present
                    attendance.is_paid = is_paid
                    attendance.notes = notes
                    attendance.save()
                
                messages.success(request, f'Посещения для {date} обновлены!')
                return redirect('attendance_list', class_id=class_id)
        else:
            # Создаем формы для каждой записи
            attendance_forms = []
            for attendance in attendances:
                form = AttendanceForm(instance=attendance, prefix=f'attendance_{attendance.id}')
                attendance_forms.append((attendance, form))
        
        # Получаем всех учеников класса для отображения в шаблоне
        students = Students.objects.filter(student_class=class_obj).order_by('surname', 'name')
        
        return render(request, 'attendance_edit.html', {
            'class_obj': class_obj,
            'date': date,
            'attendance_forms': attendance_forms,
            'students': students,
            'title': f'Редактировать посещения на {date}'
        })
    except Class.DoesNotExist:
        messages.error(request, 'Класс не найден')
        return redirect('class_list')


@login_required
def attendance_delete(request, class_id, date):
    """Удаление записей посещения для определенной даты"""
    try:
        class_obj = Class.objects.get(id=class_id)
        # Проверяем, что учитель имеет доступ к этому классу
        if class_obj.teacher != request.user.teacher_profile:
            return HttpResponseForbidden("У вас нет доступа к этому классу")
        
        # Удаляем все записи для этой даты
        deleted_count = Attendance.objects.filter(
            class_group=class_obj,
            date=date
        ).delete()[0]
        
        messages.success(request, f'Удалено {deleted_count} записей посещения для {date}')
        return redirect('attendance_list', class_id=class_id)
    except Class.DoesNotExist:
        messages.error(request, 'Класс не найден')
        return redirect('class_list')


@login_required
def payment_settings_edit(request, class_id):
    """Редактирование настроек оплаты для класса"""
    try:
        class_obj = Class.objects.get(id=class_id)
        # Проверяем, что учитель имеет доступ к этому классу
        if class_obj.teacher != request.user.teacher_profile:
            return HttpResponseForbidden("У вас нет доступа к этому классу")
        
        # Получаем или создаем настройки оплаты
        payment_settings, created = PaymentSettings.objects.get_or_create(
            class_group=class_obj,
            defaults={'payment_day': 15}
        )
        
        if request.method == 'POST':
            form = PaymentSettingsForm(request.POST, instance=payment_settings)
            if form.is_valid():
                form.save()
                messages.success(request, 'Настройки оплаты обновлены!')
                return redirect('attendance_list', class_id=class_id)
        else:
            form = PaymentSettingsForm(instance=payment_settings)
        
        return render(request, 'payment_settings_form.html', {
            'form': form,
            'class_obj': class_obj,
            'title': 'Настройки оплаты'
        })
    except Class.DoesNotExist:
        messages.error(request, 'Класс не найден')
        return redirect('class_list')


@handle_errors
def student_attendance_list(request):
    """Список посещений для ученика"""
    try:
        # Получаем ID ученика из сессии
        student_id = request.session.get('student_id')
        if not student_id:
            return redirect('student_login')
        
        student = Students.objects.get(id=student_id)
        class_obj = student.student_class
        
        # Проверяем, что у ученика есть класс
        if not class_obj:
            messages.error(request, 'Ученик не привязан к классу')
            return redirect('student_login')
        
        # Получаем стоимость за занятие из класса
        lesson_fee = getattr(class_obj, 'lesson_fee', 0) or 0
        
        # Получаем все посещения ученика в этом классе
        attendances = Attendance.objects.filter(
            student=student,
            class_group=class_obj
        ).order_by('-date')
        
        # Получаем настройки оплаты для класса
        try:
            payment_settings = PaymentSettings.objects.get(class_group=class_obj)
        except PaymentSettings.DoesNotExist:
            payment_settings = PaymentSettings.objects.create(
                class_group=class_obj,
                payment_day=15
            )
        
        # Группируем посещения по месяцам для создания табеля
        from itertools import groupby
        from operator import attrgetter
        
        # Сортируем по дате для группировки
        attendances_sorted = sorted(attendances, key=attrgetter('date'))
        
        # Группируем по месяцу и году
        monthly_attendances = {}
        for attendance in attendances_sorted:
            month_key = (attendance.date.year, attendance.date.month)
            if month_key not in monthly_attendances:
                monthly_attendances[month_key] = []
            monthly_attendances[month_key].append(attendance)
        
        # Создаем структуру табеля
        attendance_table = {}
        
        # Проверяем, что есть данные для группировки
        if monthly_attendances:
            for (year, month), month_attendances_list in monthly_attendances.items():
                month_name = f"{year}-{month:02d}"
                
                # Расчет оплаты для каждого месяца
                total_lessons = len(month_attendances_list)
                attended_lessons = sum(1 for a in month_attendances_list if a.is_present)
                paid_lessons = sum(1 for a in month_attendances_list if a.is_paid)
                carried_over = sum(1 for a in month_attendances_list if a.payment_carried_over)
                
                # Расчет суммы оплаты для месяца по количеству занятий
                month_payment = attended_lessons * lesson_fee if lesson_fee > 0 else 0
                
                attendance_table[month_name] = {
                    'year': year,
                    'month': month,
                    'attendances': month_attendances_list,
                    'total_lessons': total_lessons,
                    'attended_lessons': attended_lessons,
                    'paid_lessons': paid_lessons,
                    'carried_over': carried_over,
                    'month_payment': month_payment,
                    'lesson_fee': lesson_fee
                }
        
        # Расчет оплаты для текущего месяца
        from datetime import datetime
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        # Получаем посещения за текущий месяц
        month_attendances = attendances.filter(
            date__month=current_month,
            date__year=current_year
        )
        
        total_lessons = month_attendances.count()
        attended_lessons = month_attendances.filter(is_present=True).count()
        paid_lessons = month_attendances.filter(is_paid=True).count()
        
        # Расчет оплаты за текущий месяц по количеству занятий
        monthly_payment = 0
        # Считаем ВСЕ занятия текущего месяца (включая пропуски)
        lessons_payment = total_lessons * lesson_fee if lesson_fee > 0 else 0
        # Вычитаем стоимость уже оплаченных занятий
        paid_lessons_cost = paid_lessons * lesson_fee if lesson_fee > 0 else 0
        current_month_payment = max(0, lessons_payment - paid_lessons_cost)
        
        # Расчет задолженности за предыдущие месяцы
        previous_months_debt = 0
        
        # Проверяем, что есть данные для расчета задолженности
        if attendance_table:
            for month_key, month_data in attendance_table.items():
                # Парсим ключ месяца (формат: "2025-08")
                try:
                    year, month = map(int, month_key.split('-'))
                except (ValueError, AttributeError):
                    continue
                
                # Пропускаем текущий месяц
                if year == current_year and month == current_month:
                    continue
                
                # Пропускаем будущие месяцы - они не должны учитываться в задолженности
                if (year > current_year) or (year == current_year and month > current_month):
                    continue
                
                # Считаем задолженность по количеству занятий в месяце
                month_lessons = month_data['total_lessons']
                month_debt = month_lessons * lesson_fee if lesson_fee > 0 else 0
                
                # Вычитаем уже оплаченные занятия
                paid_in_month = month_data['paid_lessons']
                # Вычитаем стоимость оплаченных занятий
                month_debt -= paid_in_month * lesson_fee if lesson_fee > 0 else 0
                
                # Добавляем к общей задолженности (только положительные значения)
                if month_debt > 0:
                    previous_months_debt += month_debt
        
        # Общая сумма к оплате
        total_payment = current_month_payment + previous_months_debt
        
        payment_info = {
            'total_lessons': total_lessons,
            'attended_lessons': attended_lessons,
            'paid_lessons': paid_lessons,
            'monthly_payment': monthly_payment,
            'lessons_payment': lessons_payment,
            'current_month_payment': current_month_payment,
            'previous_months_debt': previous_months_debt,
            'total_payment': total_payment,
            'lesson_fee': lesson_fee,
            'current_month': current_month,
            'current_year': current_year,
            'paid_lessons_cost': paid_lessons * lesson_fee if lesson_fee > 0 else 0
        }
        
        return render(request, 'student_attendance_list.html', {
            'student': student,
            'class_obj': class_obj,
            'attendances': attendances,
            'attendance_table': attendance_table,
            'payment_info': payment_info
        })
    except Students.DoesNotExist:
        return redirect('student_login')

@login_required
def monthly_schedule_create(request, class_id):
    """Создание месячного расписания занятий"""
    try:
        class_obj = Class.objects.get(id=class_id)
        # Проверяем, что учитель имеет доступ к этому классу
        if class_obj.teacher != request.user.teacher_profile:
            return HttpResponseForbidden("У вас нет доступа к этому классу")
        
        if request.method == 'POST':
            form = MonthlyScheduleForm(request.POST)
            if form.is_valid():
                month = int(form.cleaned_data['month'])
                year = int(form.cleaned_data['year'])
                auto_generate = form.cleaned_data['auto_generate']
                
                # Проверяем, не существует ли уже расписание для этого месяца
                if MonthlySchedule.objects.filter(class_group=class_obj, month=month, year=year).exists():
                    messages.warning(request, f'Расписание для {month}/{year} уже существует')
                    return redirect('monthly_schedule_list', class_id=class_id)
                
                # Создаем месячное расписание
                monthly_schedule = MonthlySchedule.objects.create(
                    class_group=class_obj,
                    month=month,
                    year=year
                )
                
                # Генерируем даты занятий
                if auto_generate:
                    # Автоматически генерируем даты на основе дней недели класса
                    from .forms import generate_lesson_dates_from_days
                    lesson_dates = generate_lesson_dates_from_days(month, year, class_obj.days)
                    
                    if not lesson_dates:
                        messages.error(request, 'Не удалось автоматически сгенерировать даты. Проверьте дни недели в настройках класса.')
                        monthly_schedule.delete()
                        return redirect('monthly_schedule_create', class_id=class_id)
                else:
                    # Ручной ввод дат
                    lesson_dates_str = form.cleaned_data['lesson_dates']
                    if not lesson_dates_str:
                        messages.error(request, 'Укажите даты занятий или включите автоматическую генерацию')
                        monthly_schedule.delete()
                        return redirect('monthly_schedule_create', class_id=class_id)
                    
                    # Парсим даты занятий
                    try:
                        lesson_dates = [int(date.strip()) for date in lesson_dates_str.split(',') if date.strip().isdigit()]
                    except ValueError:
                        messages.error(request, 'Неверный формат дат')
                        monthly_schedule.delete()
                        return redirect('monthly_schedule_create', class_id=class_id)
                
                # Получаем всех учеников класса
                students = Students.objects.filter(student_class=class_obj)
                
                # Проверяем, есть ли ученики в классе
                if not students.exists():
                    messages.error(request, f'В классе "{class_obj.name}" нет учеников. Сначала добавьте учеников в класс, а затем создавайте расписание.')
                    return redirect('student_create_in_class', class_id=class_id)
                
                # Создаем записи посещения для всех дат и учеников
                created_count = 0
                for day in lesson_dates:
                    try:
                        # Проверяем, что дата валидна для указанного месяца и года
                        from datetime import date
                        lesson_date = date(year, month, day)
                        
                        for student in students:
                            Attendance.objects.create(
                                student=student,
                                class_group=class_obj,
                                monthly_schedule=monthly_schedule,
                                date=lesson_date,
                                is_present=True,
                                is_paid=False,
                                payment_carried_over=False
                            )
                        created_count += 1
                    except ValueError:
                        # Пропускаем невалидные даты
                        continue
                
                if created_count > 0:
                    messages.success(request, f'Месячное расписание создано! Создано {created_count} занятий')
                    return redirect('monthly_schedule_edit', class_id=class_id, schedule_id=monthly_schedule.id)
                else:
                    messages.error(request, 'Не удалось создать ни одного занятия')
                    monthly_schedule.delete()
                    return redirect('monthly_schedule_create', class_id=class_id)
        else:
            form = MonthlyScheduleForm()
            # Устанавливаем текущий месяц и год по умолчанию
            from datetime import datetime
            now = datetime.now()
            form.fields['month'].initial = now.month
            form.fields['year'].initial = now.year
        
        # Получаем всех учеников класса
        students = Students.objects.filter(student_class=class_obj).order_by('surname', 'name')
        
        # Проверяем, есть ли ученики в классе
        if not students.exists():
            messages.warning(request, f'В классе "{class_obj.name}" нет учеников. Сначала добавьте учеников в класс, а затем создавайте расписание.')
            return redirect('student_create_in_class', class_id=class_id)
        
        return render(request, 'monthly_schedule_create.html', {
            'form': form,
            'class_obj': class_obj,
            'students': students,
            'title': 'Создать месячное расписание'
        })
    except Class.DoesNotExist:
        messages.error(request, 'Класс не найден')
        return redirect('class_list')


@login_required
def monthly_schedule_list(request, class_id):
    """Список месячных расписаний для класса"""
    try:
        class_obj = Class.objects.get(id=class_id)
        # Проверяем, что учитель имеет доступ к этому классу
        if class_obj.teacher != request.user.teacher_profile:
            return HttpResponseForbidden("У вас нет доступа к этому классу")
        
        # Получаем все месячные расписания для класса
        monthly_schedules = MonthlySchedule.objects.filter(
            class_group=class_obj
        ).order_by('-year', '-month')
        
        # Получаем всех учеников класса
        students = Students.objects.filter(student_class=class_obj).order_by('surname', 'name')
        
        # Получаем настройки оплаты
        payment_settings, created = PaymentSettings.objects.get_or_create(
            class_group=class_obj,
            defaults={
                'payment_day': 15
            }
        )
        
        context = {
            'class_obj': class_obj,
            'students': students,
            'monthly_schedules': monthly_schedules,
            'payment_settings': payment_settings,
        }
        return render(request, 'monthly_schedule_list.html', context)
    except Class.DoesNotExist:
        messages.error(request, 'Класс не найден')
        return redirect('class_list')


@login_required
def monthly_schedule_edit(request, class_id, schedule_id):
    """Редактирование месячного расписания"""
    try:
        class_obj = Class.objects.get(id=class_id)
        monthly_schedule = MonthlySchedule.objects.get(id=schedule_id, class_group=class_obj)
        
        # Проверяем, что учитель имеет доступ к этому классу
        if class_obj.teacher != request.user.teacher_profile:
            return HttpResponseForbidden("У вас нет доступа к этому классу")
        
        # Получаем всех учеников класса
        students = Students.objects.filter(student_class=class_obj).order_by('surname', 'name')
        
        # Получаем уникальные даты занятий для этого расписания
        lesson_dates = Attendance.objects.filter(
            monthly_schedule=monthly_schedule
        ).values_list('date', flat=True).distinct().order_by('date')
        
        if request.method == 'POST':
            # Обрабатываем POST запрос
            forms_valid = True
            attendance_forms = []
            
            for student in students:
                for date in lesson_dates:
                    # Получаем или создаем запись посещения
                    attendance, created = Attendance.objects.get_or_create(
                        student=student,
                        monthly_schedule=monthly_schedule,
                        date=date,
                        defaults={
                            'is_present': True,
                            'is_paid': False,
                            'payment_carried_over': False
                        }
                    )
                    
                    form = MonthlyAttendanceForm(request.POST, instance=attendance, 
                                               prefix=f'attendance_{student.id}_{date.strftime("%Y%m%d")}')
                    if not form.is_valid():
                        forms_valid = False
                        break
                    attendance_forms.append((attendance, form))
                
                if not forms_valid:
                    break
            
            if forms_valid:
                for attendance, form in attendance_forms:
                    form.save()
                
                messages.success(request, f'Расписание на {monthly_schedule} обновлено!')
                return redirect('monthly_schedule_list', class_id=class_id)
        else:
            # Создаем формы для каждой комбинации ученик-дата
            attendance_forms = []
            for student in students:
                for date in lesson_dates:
                    # Получаем или создаем запись посещения
                    attendance, created = Attendance.objects.get_or_create(
                        student=student,
                        monthly_schedule=monthly_schedule,
                        date=date,
                        defaults={
                            'is_present': True,
                            'is_paid': False,
                            'payment_carried_over': False
                        }
                    )
                    
                    form = MonthlyAttendanceForm(instance=attendance, 
                                               prefix=f'attendance_{student.id}_{date.strftime("%Y%m%d")}')
                    attendance_forms.append((student, date, attendance, form))
        
        return render(request, 'monthly_schedule_edit.html', {
            'class_obj': class_obj,
            'monthly_schedule': monthly_schedule,
            'attendance_forms': attendance_forms,
            'students': students,
            'lesson_dates': lesson_dates,
            'title': f'Редактировать расписание на {monthly_schedule}'
        })
    except (Class.DoesNotExist, MonthlySchedule.DoesNotExist):
        messages.error(request, 'Класс или расписание не найдено')
        return redirect('class_list')


@login_required
def monthly_schedule_delete(request, class_id, schedule_id):
    """Удаление месячного расписания"""
    try:
        class_obj = Class.objects.get(id=class_id)
        monthly_schedule = MonthlySchedule.objects.get(id=schedule_id, class_group=class_obj)
        
        # Проверяем, что учитель имеет доступ к этому классу
        if class_obj.teacher != request.user.teacher_profile:
            return HttpResponseForbidden("У вас нет доступа к этому классу")
        
        # Удаляем все записи посещения для этого расписания
        deleted_count = Attendance.objects.filter(
            monthly_schedule=monthly_schedule
        ).delete()[0]
        
        # Удаляем само расписание
        monthly_schedule.delete()
        
        messages.success(request, f'Удалено месячное расписание и {deleted_count} записей посещения')
        return redirect('monthly_schedule_list', class_id=class_id)
    except (Class.DoesNotExist, MonthlySchedule.DoesNotExist):
        messages.error(request, 'Класс или расписание не найдено')
        return redirect('class_list')


@login_required
def carry_over_payments(request, class_id, schedule_id):
    """Перенос неоплаченных занятий на следующий месяц"""
    try:
        class_obj = Class.objects.get(id=class_id)
        monthly_schedule = MonthlySchedule.objects.get(id=schedule_id, class_group=class_obj)
        
        # Проверяем, что учитель имеет доступ к этому классу
        if class_obj.teacher != request.user.teacher_profile:
            return HttpResponseForbidden("У вас нет доступа к этому классу")
        
        if request.method == 'POST':
            # Получаем все неоплаченные занятия
            unpaid_attendances = Attendance.objects.filter(
                monthly_schedule=monthly_schedule,
                is_present=True,
                is_paid=False
            )
            
            if unpaid_attendances.exists():
                # Создаем следующий месяц
                next_month = monthly_schedule.month + 1
                next_year = monthly_schedule.year
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                
                # Создаем или получаем расписание на следующий месяц
                next_schedule, created = MonthlySchedule.objects.get_or_create(
                    class_group=class_obj,
                    month=next_month,
                    year=next_year
                )
                
                # Переносим неоплаченные занятия
                carried_over_count = 0
                for attendance in unpaid_attendances:
                    # Создаем новую запись на следующий месяц
                    new_attendance = Attendance.objects.create(
                        student=attendance.student,
                        class_group=class_obj,
                        monthly_schedule=next_schedule,
                        date=attendance.date.replace(month=next_month, year=next_year),
                        is_present=True,
                        is_paid=False,
                        payment_carried_over=True,
                        notes=f"Перенесено с {monthly_schedule}"
                    )
                    carried_over_count += 1
                
                messages.success(request, f'Перенесено {carried_over_count} неоплаченных занятий на {next_schedule}')
            else:
                messages.info(request, 'Нет неоплаченных занятий для переноса')
            
            return redirect('monthly_schedule_list', class_id=class_id)
        
        return render(request, 'carry_over_payments.html', {
            'class_obj': class_obj,
            'monthly_schedule': monthly_schedule,
            'title': 'Перенос неоплаченных занятий'
        })
    except (Class.DoesNotExist, MonthlySchedule.DoesNotExist):
        messages.error(request, 'Класс или расписание не найдено')
        return redirect('class_list')


# делаем функцию определения колонок, return добавим в рендер, колонки обозначают разряд числа и будут добавляться в переменную
# columns, в зависимости от числа, каждая колонка должна ставить список в нужном порядке
def generate_abacus_columns(number):
    # Список для всех колонок
    columns = []

    while number > 0:
        digit = number % 10

        if digit == 0:
            column = [[1, 0], [0, 1, 1, 1, 1]]
        elif digit == 1:
            column = [[1, 0], [1, 0, 1, 1, 1]]
        elif digit == 2:
            column = [[1, 0], [1, 1, 0, 1, 1]]
        elif digit == 3:
            column = [[1, 0], [1, 1, 1, 0, 1]]
        elif digit == 4:
            column = [[1, 0], [1, 1, 1, 1, 0]]
        elif digit == 5:
            column = [[0, 1], [0, 1, 1, 1, 1]]
        elif digit == 6:
            column = [[0, 1], [1, 0, 1, 1, 1]]
        elif digit == 7:
            column = [[0, 1], [1, 1, 0, 1, 1]]
        elif digit == 8:
            column = [[0, 1], [1, 1, 1, 0, 1]]
        elif digit == 9:
            column = [[0, 1], [1, 1, 1, 1, 0]]

        columns.insert(0, column)  # Вставляем колонку в начало (от младшего к старшему разряду)
        number //= 10

    return columns


def flashcards(request, mode):
    """
    Обрабатывает GET и POST запросы для страницы с флешкартами.
    GET — начальная загрузка формы.
    POST — обработка данных формы, генерация случайных чисел и колонок абакуса.
    """
    # Проверяем авторизацию ученика или учителя
    if not request.session.get('student_id') and not (hasattr(request.user, 'teacher_profile') and request.user.teacher_profile.status == 'approved'):
        return redirect('student_login')
    
    # Если пользователь только открыл страницу, обрабатываем GET-запрос
    if request.method == 'GET':
        # Отправляем шаблону flashcards.html данные с указанием, что нужно показать форму выбора параметров
        return render(request, 'flashcards.html', {
            "mode": 1  # Режим формы (выбор настроек)
        })
    
    # Если пользователь отправил форму с параметрами, обрабатываем POST-запрос
    if request.method == 'POST':
        # Проверяем, является ли это переходом от обратного отсчета к показу абакуса
        if request.POST.get('start_game'):
            return render(request, 'flashcards.html', {
                "mode": 2,           # Режим отображения абакуса
                "columns_list": request.session.get('flashcards_columns', []),
                "numbers": request.session.get('flashcards_numbers', []),
                "speed": request.session.get('flashcards_speed', 1.0)
            })
        
        # Проверяем, является ли это проверкой ответа
        if request.POST.get('check_answer'):
            # Получаем ответ пользователя
            try:
                user_answer = int(request.POST.get('user_answer'))
            except (TypeError, ValueError):
                return render(request, 'flashcards.html', {
                    "mode": 3,
                    "error": "Введите корректное число."
                })
            
            # Получаем правильную сумму из сессии
            numbers = request.session.get('flashcards_numbers', [])
            if not numbers:
                return render(request, 'flashcards.html', {
                    "mode": 3,
                    "error": "Сессия истекла. Попробуйте начать заново."
                })
            
            correct_sum = sum(numbers)
            is_correct = (user_answer == correct_sum)
            
            # Переходим в финальный режим (mode = 3) — вывод результата
            return render(request, 'flashcards.html', {
                "mode": 3,
                "is_correct": is_correct,
                "correct_sum": correct_sum,
                "user_answer": user_answer,
                "numbers": numbers
            })
        
        # Обычная обработка формы настроек
        # Получаем уровень сложности из формы и конвертируем в целое число
        difficult_level = int(request.POST.get('difficult', 1))
        # Получаем скорость показа абакуса из формы и конвертируем в число с плавающей точкой
        speed = float(request.POST.get('speed', 1.0))
        # Получаем количество чисел, которые нужно сгенерировать
        quantity = int(request.POST.get('quantity', 10))
        # Получаем максимально допустимую цифру для числа
        max_digit = int(request.POST.get('max_digit', 9))
        
        # Словарь, где для каждого уровня сложности задан свой диапазон чисел
        difficulty_ranges = {
            1: (1, 10),      # Простой уровень — числа от 1 до 9
            2: (10, 100),    # Средний уровень — числа от 10 до 99
            3: (100, 1000),  # Сложный уровень — числа от 100 до 999
            4: (1000, 10000) # Очень сложный уровень — числа от 1000 до 9999
        }
        
        # Извлекаем минимальное и максимальное значение диапазона для выбранного уровня сложности
        min_val, max_val = difficulty_ranges.get(difficult_level, (1, 10))
        
        # Инициализируем пустой список для хранения итоговых чисел
        numbers = []
        
        # Цикл для генерации заданного количества чисел
        while len(numbers) < quantity:
            # Генерируем случайное число в диапазоне сложности
            num = random.randint(min_val, max_val - 1)
            # Проверяем каждую цифру числа:
            # если каждая цифра меньше или равна max_digit — добавляем число в список
            if all(int(digit) <= max_digit for digit in str(num)):
                numbers.append(num)
        
        # После формирования списка чисел создаём список представлений абакуса для каждого числа
        columns_list = [generate_abacus_columns(number) for number in numbers]
        
        # Сохраняем данные в сессии для возможного использования в будущем
        request.session['flashcards_numbers'] = numbers
        request.session['flashcards_columns'] = columns_list
        request.session['flashcards_speed'] = speed
        request.session['flashcards_difficult_level'] = difficult_level
        
        # Передаём готовые данные в шаблон для отображения абакуса на странице
        return render(request, 'flashcards.html', {
            "mode": 2.5,         # Режим обратного отсчета перед показом абакуса
            "columns_list": columns_list,  # Список готовых колонок для каждого числа
            "numbers": numbers,   # Список чисел для проверки или вывода
            "speed": speed        # Скорость показа абакусов, передаём в шаблон для анимации
        })

@login_required
def configure_class_games(request, class_id):
    """Настройка доступности игр для класса"""
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, 'Доступ разрешен только учителям')
        return redirect('index')
    
    try:
        class_obj = Class.objects.get(id=class_id, teacher=request.user.teacher_profile)
    except Class.DoesNotExist:
        messages.error(request, 'Класс не найден')
        return redirect('class_list')
    
    if request.method == 'POST':
        # Обработка формы - получаем все игры сразу
        games = request.POST.getlist('games')
        enabled_list = request.POST.getlist('enabled')
        
        print(f"DEBUG: Получены игры: {games}")
        print(f"DEBUG: Получены состояния: {enabled_list}")
        
        if games and enabled_list:
            # Обновляем доступ ко всем играм
            for i, game_code in enumerate(games):
                if i < len(enabled_list):
                    is_enabled = enabled_list[i] == 'true'
                    print(f"DEBUG: Обновляем игру {game_code} -> {is_enabled}")
                    
                    # Создаем или обновляем доступ к игре
                    game_access, created = ClassGameAccess.objects.get_or_create(
                        class_group=class_obj,
                        game=game_code,
                        defaults={'is_enabled': is_enabled}
                    )
                    if not created:
                        game_access.is_enabled = is_enabled
                        game_access.save()
                    
                    print(f"DEBUG: {'Создана' if created else 'Обновлена'} запись для игры {game_code}")
            
            messages.success(request, f'Настройки игр для класса обновлены')
            return redirect('configure_class_games', class_id=class_id)
    
    # Получаем все доступные игры
    available_games = ClassGameAccess.GAME_CHOICES
    
    # Получаем текущие настройки для класса
    current_access = {}
    print(f"DEBUG: Получаем настройки игр для класса {class_obj.name}")
    for game_code, game_name in available_games:
        try:
            access = ClassGameAccess.objects.get(class_group=class_obj, game=game_code)
            current_access[game_code] = access.is_enabled
            print(f"DEBUG: Игра {game_code} -> {access.is_enabled}")
        except ClassGameAccess.DoesNotExist:
            current_access[game_code] = False
            print(f"DEBUG: Игра {game_code} -> не найдена в БД")
    
    print(f"DEBUG: Итоговые настройки: {current_access}")
    
    context = {
        'class_obj': class_obj,
        'available_games': available_games,
        'current_access': current_access,
    }
    
    return render(request, 'configure_class_games.html', context)

@login_required
def attendance_update(request):
    """Обновление посещений через AJAX"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            
            student_id = data.get('student_id')
            date = data.get('date')
            update_type = data.get('type')  # 'attendance' или 'payment'
            value = data.get('value')
            
            if not all([student_id, date, update_type, value is not None]):
                return JsonResponse({'success': False, 'error': 'Не все параметры переданы'})
            
            # Получаем студента
            try:
                student = Students.objects.get(id=student_id)
            except Students.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Студент не найден'})
            
            # Проверяем, что учитель имеет доступ к классу студента
            if not hasattr(request.user, 'teacher_profile') or student.student_class.teacher != request.user.teacher_profile:
                return JsonResponse({'success': False, 'error': 'Нет доступа к этому классу'})
            
            # Получаем или создаем запись посещения
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                class_group=student.student_class,
                date=date,
                defaults={
                    'is_present': False,
                    'is_paid': False,
                    'notes': ''
                }
            )
            
            # Обновляем соответствующее поле
            if update_type == 'attendance':
                attendance.is_present = value
            elif update_type == 'payment':
                attendance.is_paid = value
            else:
                return JsonResponse({'success': False, 'error': 'Неверный тип обновления'})
            
            attendance.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'Обновлено: {update_type} = {value}',
                'attendance_id': attendance.id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Неверный формат JSON'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Только POST запросы'})

def save_game_settings(user, game_type, settings_data):
    """Сохраняет настройки игры для пользователя"""
    try:
        game_settings, created = GameSettings.objects.get_or_create(
            user=user,
            game_type=game_type,
            defaults={'settings_data': settings_data}
        )
        if not created:
            game_settings.settings_data = settings_data
            game_settings.save()
        return True
    except Exception as e:
        print(f"Ошибка сохранения настроек: {e}")
        return False

def load_game_settings(user, game_type):
    """Загружает настройки игры для пользователя"""
    try:
        game_settings = GameSettings.objects.filter(
            user=user,
            game_type=game_type
        ).first()
        return game_settings.settings_data if game_settings else None
    except Exception as e:
        print(f"Ошибка загрузки настроек: {e}")
        return None

def multiplication_table(request):
    """
    Представление для игры "Таблица умножения"
    """
    # Проверяем авторизацию ученика или учителя
    if not request.session.get('student_id') and not (hasattr(request.user, 'teacher_profile') and request.user.teacher_profile.status == 'approved'):
        return redirect('student_login')
    
    return render(request, 'multiplication_table.html')


def brothers_game(request):
    """
    Представление для игры "Братья"
    """
    # Проверяем авторизацию ученика или учителя
    if not request.session.get('student_id') and not (hasattr(request.user, 'teacher_profile') and request.user.teacher_profile.status == 'approved'):
        return redirect('student_login')
    
    return render(request, 'brothers_game.html')