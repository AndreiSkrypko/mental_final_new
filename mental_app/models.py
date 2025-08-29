from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class TeacherProfile(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('approved', 'Подтвержден'),
        ('rejected', 'Отклонен'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    school = models.CharField(max_length=100, blank=True, null=True)
    subject = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.user.get_full_name()} - {self.get_status_display()}'
    
    class Meta:
        verbose_name = 'Профиль учителя'
        verbose_name_plural = 'Профили учителей'

class Class(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название класса', help_text='Например: "А", "Б", "В", "1А", "2Б", "Математический", "Гуманитарный"')
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='classes', verbose_name='Учитель')
    time = models.TimeField(verbose_name='Время занятий', help_text='Время начала занятий')
    days = models.CharField(max_length=100, verbose_name='Дни занятий', help_text='Например: "Пн, Ср, Пт" или "Вторник, Четверг"')
    academic_year = models.CharField(max_length=20, verbose_name='Учебный год', help_text='Например: 2024-2025, 2024/2025, 2024')
    lesson_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Стоимость за занятие', help_text='Стоимость одного занятия в рублях')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.name} - {self.time.strftime("%H:%M")} ({self.teacher.user.get_full_name()})'
    
    class Meta:
        verbose_name = 'Класс'
        verbose_name_plural = 'Классы'
        unique_together = ['name', 'teacher', 'academic_year']

class Students(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя')
    surname = models.CharField(max_length=50, verbose_name='Фамилия', default='')
    age = models.IntegerField(verbose_name='Возраст')
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students', verbose_name='Класс', null=True, blank=True)
    
    # Поля для информации о родителе
    parent_first_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Имя родителя')
    parent_last_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Фамилия родителя')
    parent_phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name='Номер телефона родителя')
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if hasattr(self, 'student_class') and self.student_class:
            return f'{self.surname} {self.name} - {self.student_class}'
        return f'{self.surname} {self.name}'
    
    class Meta:
        verbose_name = 'Ученик'
        verbose_name_plural = 'Ученики'

class StudentAccount(models.Model):
    student = models.OneToOneField(Students, on_delete=models.CASCADE, related_name='account', verbose_name='Ученик')
    username = models.CharField(max_length=50, unique=True, verbose_name='Логин')
    password = models.CharField(max_length=128, verbose_name='Пароль')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='Последний вход')
    
    def __str__(self):
        return f'{self.student.surname} {self.student.name} ({self.username})'
    
    class Meta:
        verbose_name = 'Аккаунт ученика'
        verbose_name_plural = 'Аккаунты учеников'

class Homework(models.Model):
    class_group = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='homeworks', verbose_name='Класс')
    title = models.CharField(max_length=200, verbose_name='Название задания')
    description = models.TextField(verbose_name='Описание задания')
    due_date = models.DateField(verbose_name='Срок выполнения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    
    def __str__(self):
        return f'{self.title} - {self.class_group.name}'
    
    class Meta:
        verbose_name = 'Домашнее задание'
        verbose_name_plural = 'Домашние задания'
        ordering = ['-created_at']


class PaymentSettings(models.Model):
    """Настройки оплаты для классов"""
    class_group = models.OneToOneField(Class, on_delete=models.CASCADE, related_name='payment_settings', verbose_name='Класс')
    monthly_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Ежемесячная плата')
    payment_day = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        default=15,
        verbose_name='День оплаты',
        help_text='День месяца, когда должна производиться оплата'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.class_group.name} - {self.monthly_fee} руб.'
    
    class Meta:
        verbose_name = 'Настройки оплаты'
        verbose_name_plural = 'Настройки оплаты'

class ClassGameAccess(models.Model):
    """Доступность игр для класса"""
    GAME_CHOICES = [
        ('multiplication_choose', 'Умножение'),
        ('square', 'Квадраты'),
        ('tricks', 'Трюки'),
        ('flashcards', 'Флэшкарты'),
        ('multiplication_base', 'Умножение от базы'),
        ('multiplication_to_20', 'Умножение до 20'),
    ]
    
    class_group = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='game_access', verbose_name='Класс')
    game = models.CharField(max_length=50, choices=GAME_CHOICES, verbose_name='Игра')
    is_enabled = models.BooleanField(default=False, verbose_name='Доступна')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        status = "доступна" if self.is_enabled else "недоступна"
        return f'{self.class_group.name} - {self.get_game_display()} ({status})'
    
    class Meta:
        verbose_name = 'Доступность игры для класса'
        verbose_name_plural = 'Доступность игр для классов'
        unique_together = ['class_group', 'game']


class MonthlySchedule(models.Model):
    """Месячное расписание занятий для класса"""
    class_group = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='monthly_schedules', verbose_name='Класс')
    month = models.IntegerField(verbose_name='Месяц (1-12)')
    year = models.IntegerField(verbose_name='Год')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        month_names = [
            'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
        ]
        return f'{month_names[self.month-1]} {self.year} - {self.class_group.name}'

    def get_unique_lesson_dates_count(self):
        """Возвращает количество уникальных дат занятий"""
        return self.attendances.values('date').distinct().count()

    def get_total_attendance_records(self):
        """Возвращает общее количество записей посещения (ученики × даты)"""
        return self.attendances.count()

    class Meta:
        verbose_name = 'Месячное расписание'
        verbose_name_plural = 'Месячные расписания'
        unique_together = ['class_group', 'month', 'year']
        ordering = ['-year', '-month']


class Attendance(models.Model):
    """Модель для учета посещения занятий учениками"""
    student = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='attendances', verbose_name='Ученик')
    class_group = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='attendances', verbose_name='Класс')
    monthly_schedule = models.ForeignKey(MonthlySchedule, on_delete=models.CASCADE, related_name='attendances', verbose_name='Месячное расписание', null=True, blank=True)
    date = models.DateField(verbose_name='Дата занятия')
    is_present = models.BooleanField(default=True, verbose_name='Присутствовал')
    is_paid = models.BooleanField(default=False, verbose_name='Оплачено')
    payment_carried_over = models.BooleanField(default=False, verbose_name='Оплата перенесена на следующий месяц')
    notes = models.TextField(blank=True, verbose_name='Примечания')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        status = "Присутствовал" if self.is_present else "Отсутствовал"
        return f'{self.student.name} {self.student.surname} - {self.date} - {status}'

    class Meta:
        verbose_name = 'Посещение'
        verbose_name_plural = 'Посещения'
        ordering = ['-date', 'student__surname', 'student__name']
        unique_together = ['student', 'date', 'class_group']

class GameSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    game_type = models.CharField(max_length=50, verbose_name="Тип игры")
    settings_data = models.JSONField(verbose_name="Данные настроек")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Настройки игры"
        verbose_name_plural = "Настройки игр"
        unique_together = ['user', 'game_type']

    def __str__(self):
        return f"Настройки {self.game_type} для {self.user.username}"
