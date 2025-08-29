# Исправление проблемы с модальными окнами

## Проблема
Модальные окна для удаления учеников и классов зависали при использовании Bootstrap 5.

## Решение
Заменил Bootstrap модальные окна на собственные, более надежные модальные окна с использованием чистого HTML, CSS и JavaScript.

## Что было исправлено

### 1. templates/students_list.html
- Заменил Bootstrap модальное окно на собственное
- Добавил функции `confirmDelete()` и `closeDeleteModal()`
- Добавил поддержку закрытия по клику вне окна и по клавише Escape

### 2. templates/class_list.html
- Аналогично заменил Bootstrap модальное окно
- Добавил те же функции и возможности

## Особенности новых модальных окон

- **Надежность**: Не зависят от внешних библиотек Bootstrap
- **Анимация**: Плавное появление с эффектом slide-in
- **Закрытие**: По кнопке, клику вне окна, клавише Escape
- **Стилизация**: Сохранен дизайн в стиле приложения
- **Адаптивность**: Работает на всех устройствах

## Функции JavaScript

```javascript
// Показать модальное окно
function confirmDelete(name, deleteUrl) {
    document.getElementById('studentName').textContent = name;
    document.getElementById('confirmDelete').href = deleteUrl;
    document.getElementById('deleteModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// Закрыть модальное окно
function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
    document.body.style.overflow = 'auto';
}
```

## CSS классы

- `.custom-modal` - основное модальное окно
- `.custom-modal-content` - содержимое модального окна
- `.custom-modal-header` - заголовок с градиентом
- `.custom-modal-body` - тело модального окна
- `.custom-modal-footer` - футер с кнопками
- `.custom-modal-close` - кнопка закрытия

## Тестирование
После внесения изменений:
1. Перейдите на страницу списка учеников
2. Нажмите кнопку удаления ученика
3. Проверьте, что модальное окно открывается и закрывается корректно
4. Аналогично протестируйте удаление класса

## Примечания
- Модальные окна теперь работают независимо от Bootstrap
- Сохранен весь функционал и дизайн
- Добавлена дополнительная надежность и удобство использования
