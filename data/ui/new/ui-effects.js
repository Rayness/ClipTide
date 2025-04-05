document.addEventListener("DOMContentLoaded", function() {
    // Анимация элементов при загрузке
    animateElements();
    
    // Обработчики для модального окна
    setupModalHandlers();
    
    // Обработчики для кнопок
    setupButtonEffects();
});

function animateElements() {
    const elements = document.querySelectorAll('.content-section, .nav-btn, .control-btn');
    elements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = `all 0.5s ease ${index * 0.1}s`;
        
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 100);
    });
}

function setupModalHandlers() {
    const modal = document.getElementById('queueModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
}

function setupButtonEffects() {
    const buttons = document.querySelectorAll('.btn, .control-btn, .icon-btn');
    buttons.forEach(button => {
        button.addEventListener('mousedown', function() {
            this.style.transform = 'scale(0.95)';
        });
        
        button.addEventListener('mouseup', function() {
            this.style.transform = 'scale(1.05)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    });
}

function closeModal() {
    document.getElementById('queueModal').style.display = 'none';
    document.body.style.overflow = '';
}

// Экспортируем функции для использования в других скриптах
window.UI = {
    closeModal
};