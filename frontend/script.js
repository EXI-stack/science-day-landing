function updateCountdown() {
    const eventDate = new Date('2025-12-20T00:00:00').getTime();
    const now = new Date().getTime();
    const distance = eventDate - now;

    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    document.getElementById('days').textContent = String(days).padStart(2, '0');
    document.getElementById('hours').textContent = String(hours).padStart(2, '0');
    document.getElementById('minutes').textContent = String(minutes).padStart(2, '0');
    document.getElementById('seconds').textContent = String(seconds).padStart(2, '0');

    if (distance < 0) {
        clearInterval(countdownTimer);
        document.getElementById('timer').innerHTML = "Мероприятие началось!";
    }
}

const countdownTimer = setInterval(updateCountdown, 1000);
updateCountdown();

const form = document.getElementById('regForm');
const resultEl = document.getElementById('result');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    resultEl.textContent = '';
    resultEl.style.color = '';

    const name = document.getElementById('name').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const age = document.getElementById('age').value.trim();

    // Валидация
    const nameRegex = /^[A-Za-zА-Яа-яЁё\s\-]+$/;
    const phoneRegex = /^\+7\d{10}$/;
    const ageNum = parseInt(age, 10);

    if (!nameRegex.test(name)) {
        showError('Имя должно содержать только буквы, пробелы и дефисы');
        return;
    }
    if (!phoneRegex.test(phone)) {
        showError('Телефон должен быть в формате +79998887766');
        return;
    }
    if (isNaN(ageNum) || ageNum < 5 || ageNum > 99) {
        showError('Возраст должен быть числом от 5 до 99');
        return;
    }

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                name: name,
                phone: phone,
                age: age
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            showSuccess('Заявка отправлена успешно!');
            form.reset();
        } else {
            showError(data.error || 'Ошибка отправки заявки');
        }
    } catch (err) {
        console.error(err);
        showError('Ошибка сети. Попробуйте еще раз.');
    }
});

function showError(message) {
    resultEl.textContent = message;
    resultEl.style.color = '#e74c3c';
}

function showSuccess(message) {
    resultEl.textContent = message;
    resultEl.style.color = '#27ae60';
}