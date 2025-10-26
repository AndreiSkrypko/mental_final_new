// Универсальные функции для показа примеров в играх

// ОПТИМИЗИРОВАННАЯ функция для переключения видимости примера (убраны тяжелые анимации)
function toggleGameExample() {
    const exampleBlock = document.getElementById('exampleBlock');
    const showExampleBtn = document.getElementById('showExampleBtn');
    
    if (exampleBlock && showExampleBtn) {
        if (exampleBlock.style.display === 'none' || exampleBlock.style.display === '') {
            // Показываем пример - мгновенно!
            exampleBlock.style.display = 'block';
            showExampleBtn.innerHTML = '<i class="fas fa-eye-slash"></i> Скрыть пример';
        } else {
            // Скрываем пример - мгновенно!
            exampleBlock.style.display = 'none';
            showExampleBtn.innerHTML = '<i class="fas fa-eye"></i> Показать пример вычислений';
        }
    }
}

// Функция для генерации простого математического выражения
function generateSimpleExpression(numbers, result) {
    if (!numbers || numbers.length === 0) {
        return '<p>Данные о числах недоступны</p>';
    }
    
    let expression = '';
    
    numbers.forEach((number, index) => {
        if (index === 0) {
            // Первое число
            expression += number >= 0 ? `+${number}` : `${number}`;
        } else {
            // Последующие числа с правильными знаками
            expression += number >= 0 ? `+${number}` : `${number}`;
        }
    });
    
    return `
        <div class="simple-expression">
            <div class="expression-line">
                <span class="expression">${expression}</span>
                <span class="equals">=</span>
                <span class="result">${result}</span>
            </div>
        </div>
    `;
}

// Функция для генерации выражения умножения
function generateMultiplicationExpression(num1, num2, result) {
    return `
        <div class="simple-expression">
            <div class="expression-line">
                <span class="expression">${num1} × ${num2}</span>
                <span class="equals">=</span>
                <span class="result">${result}</span>
            </div>
        </div>
    `;
}

// Функция для генерации выражения квадрата
function generateSquareExpression(number, result) {
    return `
        <div class="simple-expression">
            <div class="expression-line">
                <span class="expression">${number}²</span>
                <span class="equals">=</span>
                <span class="result">${result}</span>
            </div>
        </div>
    `;
}
