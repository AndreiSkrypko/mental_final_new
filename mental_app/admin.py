from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Students, Class, TeacherProfile, StudentAccount, 
    Homework, PaymentSettings, ClassGameAccess, 
    Attendance, GameSettings
)

class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'school', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'school']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email', 'school']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'phone', 'school', 'subject')
        }),
        ('Статус', {
            'fields': ('status',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'time', 'days', 'teacher', 'academic_year', 'lesson_fee', 'created_at']
    list_filter = ['time', 'days', 'academic_year', 'created_at']
    search_fields = ['name', 'teacher__user__first_name', 'teacher__user__last_name']
    readonly_fields = ['created_at']
    list_editable = ['lesson_fee']

class StudentsAdmin(admin.ModelAdmin):
    list_display = ['surname', 'name', 'age', 'student_class', 'parent_phone_number']
    list_filter = ['age', 'student_class', 'created_at']
    search_fields = ['name', 'surname', 'parent_first_name', 'parent_last_name']
    readonly_fields = ['created_at', 'updated_at']

class StudentAccountAdmin(admin.ModelAdmin):
    list_display = ['student', 'username', 'is_active', 'created_at', 'last_login']
    list_filter = ['is_active', 'created_at', 'last_login']
    search_fields = ['username', 'student__name', 'student__surname']
    readonly_fields = ['created_at', 'last_login']
    list_editable = ['is_active']

class HomeworkAdmin(admin.ModelAdmin):
    list_display = ['title', 'class_group', 'due_date', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'due_date', 'class_group']
    search_fields = ['title', 'description', 'class_group__name']
    list_editable = ['is_active']
    date_hierarchy = 'created_at'


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_group', 'monthly_schedule', 'date', 'is_present', 'is_paid', 'payment_carried_over', 'created_at']
    list_filter = ['is_present', 'is_paid', 'payment_carried_over', 'date', 'class_group', 'monthly_schedule', 'created_at']
    search_fields = ['student__name', 'student__surname', 'class_group__name']
    list_editable = ['is_present', 'is_paid', 'payment_carried_over']
    date_hierarchy = 'date'
    ordering = ['-date', 'student__surname', 'student__name']


class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ['class_group', 'monthly_fee', 'payment_day', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['class_group__name']
    list_editable = ['is_active', 'monthly_fee', 'payment_day']


# Убираем MonthlyScheduleAdmin, так как модель больше не существует
# class MonthlyScheduleAdmin(admin.ModelAdmin):
#     list_display = ['class_group', 'start_date', 'end_date', 'weekdays']
#     list_filter = ['class_group', 'start_date', 'end_date']
#     search_fields = ['class_group__name']
#     date_hierarchy = 'start_date'


# Регистрируем модели
admin.site.register(TeacherProfile, TeacherProfileAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Students, StudentsAdmin)
admin.site.register(StudentAccount, StudentAccountAdmin)
admin.site.register(Homework, HomeworkAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(PaymentSettings, PaymentSettingsAdmin)
# admin.site.register(MonthlySchedule, MonthlyScheduleAdmin) # Удалено
admin.site.register(ClassGameAccess, admin.ModelAdmin)

@admin.register(GameSettings)
class GameSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'game_type', 'updated_at']
    list_filter = ['game_type', 'updated_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']

# Отменяем регистрацию стандартной модели User, так как мы будем использовать TeacherProfile
# admin.site.unregister(User)
