from django.contrib import admin
from django.urls import path
from mental_app import views

# --- 1. Объяснение создания маршрута --- :
# EN - path('admin/', admin.site.urls)
# RU - ФункцияСозданияМаршрута(URL, МетодОбработкиURL, ИмяМаршрута)

# --- 2. Объяснение ДИНАМИЧЕСКОЙ части в маршруте ---
# PATH: Динамическое место в URL - <int:product_id> <ТипДанных:ИмяПеременной>
# Возможные типы данных: str, int, slug, uuid, path
# Пример: path('products/<int:product_id>/<str:name>', ...)

# --- 3. Передача данных может быть 2-умя способами: ---
# 1. Передача ДАННЫХ через [интернет-адрес] - http://127.0.0.1:8000/products/8/Samsung
#    Данные будут находиться: В аргументах функции обработки URL
# 2. Передача ДАННЫХ [по строке запроса] - http://127.0.0.1:products?product_id=3&name=Samsung
#    Данные будут находиться: В первом аргументе "request" функции обработки URL - request.GET.get()


urlpatterns = [
    path('admin/', admin.site.urls),  # Стандартный путь к административной панели Django

    path('', views.index, name='index'),  # Главная страница (обрабатывается функцией index)

    # Маршруты для учителей
    path('teacher/register/', views.teacher_register, name='teacher_register'),
    path('teacher/pending-approval/', views.teacher_pending_approval, name='teacher_pending_approval'),
    path('teacher/login/', views.teacher_login, name='teacher_login'),
    path('teacher/logout/', views.teacher_logout, name='teacher_logout'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/profile/edit/', views.teacher_profile_edit, name='teacher_profile_edit'),
    
    # Маршруты для классов
    path('teacher/classes/', views.class_list, name='class_list'),
    path('teacher/classes/create/', views.class_create, name='class_create'),
    path('teacher/classes/<int:class_id>/edit/', views.class_edit, name='class_edit'),
    path('teacher/classes/<int:class_id>/delete/', views.class_delete, name='class_delete'),
    
    # Маршруты для учеников
    path('teacher/students/', views.students_list, name='students_list'),
    path('teacher/classes/<int:class_id>/students/', views.students_list, name='students_list_by_class'),
    path('teacher/students/create/', views.student_create, name='student_create'),
    path('teacher/classes/<int:class_id>/students/create/', views.student_create, name='student_create_in_class'),
    path('teacher/students/<int:student_id>/edit/', views.student_edit, name='student_edit'),
    path('teacher/students/<int:student_id>/delete/', views.student_delete, name='student_delete'),
    
    # Маршруты для аккаунтов учеников
    path('teacher/students/<int:student_id>/create-account/', views.create_student_account, name='create_student_account'),
    path('teacher/students/<int:student_id>/delete-account/', views.delete_student_account, name='delete_student_account'),
    
    # Маршруты для домашних заданий
    path('teacher/classes/<int:class_id>/homework/', views.homework_list, name='homework_list'),
    path('teacher/classes/<int:class_id>/homework/create/', views.homework_create, name='homework_create'),
    path('teacher/homework/<int:homework_id>/edit/', views.homework_edit, name='homework_edit'),
    path('teacher/homework/<int:homework_id>/delete/', views.homework_delete, name='homework_delete'),

    # Маршруты для посещений
    path('teacher/classes/<int:class_id>/attendance/', views.attendance_list, name='attendance_list'),
    path('teacher/classes/<int:class_id>/attendance/create/', views.attendance_create, name='attendance_create'),
    path('teacher/classes/<int:class_id>/attendance/<str:date>/edit/', views.attendance_edit, name='attendance_edit'),
    path('teacher/classes/<int:class_id>/attendance/<str:date>/delete/', views.attendance_delete, name='attendance_delete'),
    path('teacher/classes/<int:class_id>/payment-settings/', views.payment_settings_edit, name='payment_settings_edit'),
    path('teacher/classes/<int:class_id>/games/', views.configure_class_games, name='configure_class_games'),
    path('teacher/attendance/update/', views.attendance_update, name='attendance_update'),
    path('teacher/classes/<int:class_id>/attendance/add-date/', views.attendance_add_date, name='attendance_add_date'),
    path('teacher/classes/<int:class_id>/attendance/delete-date/', views.attendance_delete_date, name='attendance_delete_date'),



    # Маршруты для учеников
    path('student/login/', views.student_login, name='student_login'),
    path('student/logout/', views.student_logout, name='student_logout'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/homework/', views.student_homework_list, name='student_homework_list'),
    path('student/attendance/', views.student_attendance_list, name='student_attendance_list'),

    path('multiplication_choose/<int:mode>/', views.multiplication_choose, name='multiplication_choose'),
    # Путь для выбора чисел, отображения примера и проверки ответа
    # <int:mode> - динамический параметр, который передается в функцию multiplication_choose

    path('multiplication_to_20/<int:mode>/', views.multiplication_to_20, name='multiplication_to_20'),

    path('square/<int:mode>/', views.square, name='square'),

    path('multiplication_base/<int:mode>/', views.multiplication_base, name='multiplication_base'),

    path('tricks/<int:mode>/', views.tricks, name='tricks'),

    path('simply/<int:mode>/', views.simply, name='simply'),

    path('flashcards/', views.flashcards, name='flashcards'),

    # Старые маршруты для обратной совместимости
    path('delete_student/<int:student_id>/', views.students_list, {'mode': 4}, name='delete_student'),
    # Новый URL для удаления
]
