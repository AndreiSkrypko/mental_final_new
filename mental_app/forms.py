from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import TeacherProfile, Class, Students, StudentAccount, Homework, Attendance, PaymentSettings, ClassGameAccess
import calendar
from datetime import datetime, date

def generate_lesson_dates_from_days(month, year, days_str):
    """
    Генерирует даты занятий на основе дней недели класса
    days_str: строка с днями недели (например: "Пн, Ср, Пт" или "Понедельник, Среда")
    """
    # Словарь для перевода дней недели
    day_mapping = {
        'пн': 0, 'понедельник': 0, 'monday': 0,
        'вт': 1, 'вторник': 1, 'tuesday': 1,
        'ср': 2, 'среда': 2, 'wednesday': 2,
        'чт': 3, 'четверг': 3, 'thursday': 3,
        'пт': 4, 'пятница': 4, 'friday': 4,
        'сб': 5, 'суббота': 5, 'saturday': 5,
        'вс': 6, 'воскресенье': 6, 'sunday': 6
    }
    
    # Парсим дни недели
    target_weekdays = set()
    for day in days_str.lower().split(','):
        day = day.strip()
        if day in day_mapping:
            target_weekdays.add(day_mapping[day])
    
    if not target_weekdays:
        return []
    
    # Получаем календарь месяца
    cal = calendar.monthcalendar(year, month)
    lesson_dates = []
    
    for week in cal:
        for i, day in enumerate(week):
            if day != 0 and i in target_weekdays:
                lesson_dates.append(day)
    
    return sorted(lesson_dates)

class TeacherRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=15, required=False, label='Телефон')
    school = forms.CharField(max_length=100, required=False, label='Школа')
    subject = forms.CharField(max_length=100, required=False, label='Предмет')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            TeacherProfile.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                school=self.cleaned_data['school'],
                subject=self.cleaned_data['subject']
            )
        return user

class TeacherLoginForm(forms.Form):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput(), label='Пароль')

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'time', 'days', 'academic_year', 'lesson_fee']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Например: А, Б, В, 1А, 2Б, Математический'
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'placeholder': 'Выберите время'
            }),
            'days': forms.TextInput(attrs={
                'placeholder': 'Например: Пн, Ср, Пт или Вторник, Четверг'
            }),
            'academic_year': forms.TextInput(attrs={
                'placeholder': '2024-2025, 2024/2025, 2024 или любой формат'
            }),
            'lesson_fee': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01'
            })
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Students
        fields = ['name', 'surname', 'age', 'parent_first_name', 'parent_last_name', 'parent_phone_number']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Введите имя ученика',
                'class': 'form-control'
            }),
            'surname': forms.TextInput(attrs={
                'placeholder': 'Введите фамилию ученика',
                'class': 'form-control'
            }),
            'age': forms.NumberInput(attrs={
                'min': '6', 
                'max': '18',
                'placeholder': 'Возраст от 6 до 18',
                'class': 'form-control'
            }),
            'parent_first_name': forms.TextInput(attrs={
                'placeholder': 'Имя родителя (необязательно)',
                'class': 'form-control'
            }),
            'parent_last_name': forms.TextInput(attrs={
                'placeholder': 'Фамилия родителя (необязательно)',
                'class': 'form-control'
            }),
            'parent_phone_number': forms.TextInput(attrs={
                'placeholder': '+375291234567 или 80291234567',
                'class': 'form-control'
            })
        }

class TeacherProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['phone', 'school', 'subject']
        widgets = {
            'phone': forms.TextInput(attrs={
                'placeholder': '+375291234567 или 80291234567'
            }),
            'school': forms.TextInput(attrs={
                'placeholder': 'Название вашей школы'
            }),
            'subject': forms.TextInput(attrs={
                'placeholder': 'Например: Математика, Физика, История'
            })
        }

class StudentAccountForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label='Пароль')
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Подтвердите пароль')
    
    class Meta:
        model = StudentAccount
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Придумайте логин для ученика',
                'class': 'form-control'
            }),
        }
    
    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Пароли не совпадают')
        
        return confirm_password
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if StudentAccount.objects.filter(username=username).exists():
            raise forms.ValidationError('Такой логин уже существует')
        return username

class StudentLoginForm(forms.Form):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={
        'placeholder': 'Введите ваш логин',
        'class': 'form-control'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Введите ваш пароль',
        'class': 'form-control'
    }), label='Пароль')

class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ['title', 'description', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Название домашнего задания',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Описание задания...',
                'class': 'form-control',
                'rows': 5
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
        labels = {
            'title': 'Название задания',
            'description': 'Описание',
            'due_date': 'Срок выполнения'
        }


class AttendanceForm(forms.ModelForm):
    """Форма для отметки посещения"""
    class Meta:
        model = Attendance
        fields = ['is_present', 'is_paid', 'notes']
        widgets = {
            'is_present': forms.CheckboxInput(attrs={
                'class': 'form-check-input attendance-checkbox'
            }),
            'is_paid': forms.CheckboxInput(attrs={
                'class': 'form-check-input payment-checkbox'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Примечания...'
            }),
        }
        labels = {
            'is_present': 'Присутствовал',
            'is_paid': 'Оплачено',
            'notes': 'Примечания'
        }


class AttendanceDateForm(forms.Form):
    """Форма для выбора даты занятия"""
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'required': True
        }),
        label='Дата занятия'
    )


class PaymentSettingsForm(forms.ModelForm):
    """Форма для настройки оплаты класса"""
    class Meta:
        model = PaymentSettings
        fields = ['payment_day']
        widgets = {
            'payment_day': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '31',
                'placeholder': '15'
            }),
        }
        labels = {
            'payment_day': 'День оплаты'
        }


class MonthlyScheduleForm(forms.Form):
    """Форма для создания месячного расписания"""
    month = forms.ChoiceField(
        choices=[
            (1, 'Январь'), (2, 'Февраль'), (3, 'Март'), (4, 'Апрель'),
            (5, 'Май'), (6, 'Июнь'), (7, 'Июль'), (8, 'Август'),
            (9, 'Сентябрь'), (10, 'Октябрь'), (11, 'Ноябрь'), (12, 'Декабрь')
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label='Месяц'
    )
    
    year = forms.IntegerField(
        min_value=2020,
        max_value=2030,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'required': True,
            'placeholder': '2025'
        }),
        label='Год'
    )
    
    auto_generate = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'auto_generate'
        }),
        label='Автоматически сгенерировать даты на основе дней недели класса',
        help_text='Если отмечено, даты будут созданы автоматически на основе дней занятий класса'
    )
    
    lesson_dates = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Введите даты занятий через запятую (например: 1, 3, 5, 8, 10, 12, 15, 17, 19, 22, 24, 26, 29, 31)',
            'id': 'lesson_dates_field'
        }),
        label='Даты занятий (вручную)',
        help_text='Укажите числа месяца, когда будут проходить занятия (через запятую). Используйте только если автоматическая генерация отключена.'
    )


class MonthlyAttendanceForm(forms.ModelForm):
    """Форма для отметки посещения и оплаты"""
    class Meta:
        model = Attendance
        fields = ['is_present', 'is_paid', 'payment_carried_over', 'notes']
        widgets = {
            'is_present': forms.CheckboxInput(attrs={
                'class': 'form-check-input attendance-checkbox'
            }),
            'is_paid': forms.CheckboxInput(attrs={
                'class': 'form-check-input payment-checkbox'
            }),
            'payment_carried_over': forms.CheckboxInput(attrs={
                'class': 'form-check-input carryover-checkbox'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Примечания...'
            }),
        }
        labels = {
            'is_present': 'Присутствовал',
            'is_paid': 'Оплачено',
            'payment_carried_over': 'Перенести на следующий месяц',
            'notes': 'Примечания'
        }

class ClassGameAccessForm(forms.ModelForm):
    """Форма для настройки доступности игр для класса"""
    class Meta:
        model = ClassGameAccess
        fields = ['game', 'is_enabled']
        widgets = {
            'game': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'game': 'Игра',
            'is_enabled': 'Доступна'
        }
