# Инструкции по применению полноэкранного режима ко всем играм

## Что изменено в игре "Просто" (simply.html)

### 1. Отсчет (mode == 2)
- Заменен `<div class="number-display">` на `<div class="countdown-fullscreen">`
- Убраны все рамки и границы
- Числа отсчета теперь занимают весь экран (25vw на больших экранах, до 50vw на мобильных)
- Добавлена анимация пульсации для чисел

### 2. Показ чисел (mode == 5)
- Заменен `<div class="number-display">` на `<div class="number-display-fullscreen">`
- Числа теперь максимально большие (30vw на больших экранах, до 50vw на мобильных)
- Убраны все рамки, тени и границы
- Прогресс-бар и счетчик сделаны миниатюрными
- Кнопки управления уменьшены

### 3. CSS стили для полноэкранного режима
Добавлены новые классы:
- `.countdown-fullscreen` - полноэкранный отсчет
- `.number-display-fullscreen` - полноэкранный показ чисел
- `.current-number-huge` - огромные числа
- `.countdown-number` - большие числа отсчета
- Адаптивные размеры для разных экранов

### 4. Озвучка с "плюс"
- Функция `speakNumber()` теперь добавляет "плюс " перед положительными числами

## Как применить к другим играм

### Для multiplication_base.html, square.html, tricks.html, flashcards.html:

1. **Заменить HTML структуру для отсчета:**
```html
<!-- Было -->
<div class="number-display">
    <div class="timer-display">
        <div>Игра начнется через:</div>
        <div class="countdown-timer" id="countdown">3</div>
    </div>
</div>

<!-- Стало -->
<div class="countdown-fullscreen">
    <div class="countdown-content">
        <div class="countdown-text">Игра начнется через:</div>
        <div class="countdown-number" id="countdown">3</div>
    </div>
</div>
```

2. **Заменить HTML структуру для показа чисел:**
```html
<!-- Было -->
<div class="number-display">
    <div class="current-number">{{ number }}</div>
</div>

<!-- Стало -->
<div class="number-display-fullscreen">
    <div class="number-content">
        <div class="current-number-huge">{{ number }}</div>
    </div>
</div>
```

3. **Добавить CSS стили:**
Скопировать все CSS стили для полноэкранного режима из `simply.html` в соответствующие файлы игр.

4. **Добавить кнопку "Выйти из игры":**
```html
<button class="exit-game-button" onclick="exitGame()">
    <span class="exit-icon">🚪</span>
    Выйти из игры
</button>
```

5. **Добавить функцию exitGame():**
```javascript
function exitGame() {
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
    }
    
    if (window.showNavbar) {
        window.showNavbar();
    }
    
    window.location.href = '/';
}
```

## Преимущества нового подхода

1. **Полноэкранный режим** - никаких рамок и границ
2. **Максимальные размеры** - числа занимают весь экран
3. **Адаптивность** - автоматически подстраивается под размер экрана
4. **Единообразие** - все игры будут выглядеть одинаково
5. **Лучшая читаемость** - числа видны издалека

## Примечания

- Используются единицы `vw` (viewport width) и `vh` (viewport height) для адаптивности
- Кнопка "Выйти из игры" остается в правом верхнем углу
- Навбар автоматически скрывается при входе в игру
- Все анимации и переходы сохранены
