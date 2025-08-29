# 🔧 Инструкция по исправлению 500 ошибки при добавлении ученика через класс

## 🎯 Проблема
На сервере возникает 500 ошибка при попытке добавить ученика **через класс**, хотя добавление ученика напрямую работает нормально.

## 🔍 Причина
В файле `mental/urls.py` отсутствуют URL-маршруты для месячного расписания, которые используются в функции `student_create` при добавлении ученика через класс.

## ✅ Решение

### 1. Обновить файл `mental/urls.py`
Добавить следующие строки в секцию URL-маршрутов (примерно после строки 75):

```python
# Маршруты для месячного расписания
path('teacher/classes/<int:class_id>/monthly-schedule/', views.monthly_schedule_list, name='monthly_schedule_list'),
path('teacher/classes/<int:class_id>/monthly-schedule/create/', views.monthly_schedule_create, name='monthly_schedule_create'),
path('teacher/classes/<int:class_id>/monthly-schedule/<int:schedule_id>/edit/', views.monthly_schedule_edit, name='monthly_schedule_edit'),
path('teacher/classes/<int:class_id>/monthly-schedule/<int:schedule_id>/delete/', views.monthly_schedule_delete, name='monthly_schedule_delete'),
path('teacher/classes/<int:class_id>/monthly-schedule/<int:schedule_id>/carry-over/', views.carry_over_payments, name='carry_over_payments'),
```

### 2. Перезапустить сервер
```bash
# Остановить сервис
sudo systemctl stop mental

# Запустить сервис
sudo systemctl start mental

# Проверить статус
sudo systemctl status mental
```

### 3. Проверить логи
```bash
# Логи Django
tail -f django.log

# Логи systemd
sudo journalctl -u mental -f

# Логи Nginx (если используется)
sudo tail -f /var/log/nginx/error.log
```

## 📋 Пошаговое выполнение

1. **Подключиться к серверу** по SSH
2. **Перейти в директорию проекта**:
   ```bash
   cd /path/to/your/project
   ```
3. **Отредактировать файл** `mental/urls.py`:
   ```bash
   nano mental/urls.py
   # или
   vim mental/urls.py
   ```
4. **Добавить недостающие URL-маршруты** (см. выше)
5. **Сохранить файл**
6. **Перезапустить сервер** (см. команды выше)
7. **Протестировать** добавление ученика через класс

## 🧪 Проверка
После исправления:
- ✅ Добавление ученика напрямую должно работать
- ✅ Добавление ученика через класс должно работать
- ✅ Редирект на создание месячного расписания должен работать

## 📝 Дополнительные рекомендации

### Проверить наличие всех необходимых представлений
Убедитесь, что в `mental_app/views.py` есть все функции:
- `monthly_schedule_list`
- `monthly_schedule_create`
- `monthly_schedule_edit`
- `monthly_schedule_delete`
- `carry_over_payments`

### Проверить права доступа
```bash
# Проверить владельца файлов
ls -la mental/urls.py

# Если нужно, изменить владельца
sudo chown www-data:www-data mental/urls.py
```

### Проверить синтаксис Python
```bash
# Проверить синтаксис файла
python -m py_compile mental/urls.py
```

## 🚨 Если проблема не решена

1. **Проверить логи Django** на наличие других ошибок
2. **Проверить версию Django** на сервере
3. **Проверить настройки базы данных**
4. **Проверить переменные окружения**

## 📞 Поддержка
Если проблема не решается, предоставьте:
- Логи Django (`django.log`)
- Логи systemd (`sudo journalctl -u mental`)
- Логи Nginx (если используется)
- Версию Django на сервере
- Содержимое файла `mental/urls.py` после изменений
