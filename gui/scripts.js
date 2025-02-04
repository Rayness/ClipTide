 // Добавляем обработчик события для кнопки
 document.getElementById('downloadBtn').addEventListener('click', function() {
    const videoUrl = document.getElementById('videoUrl').value;

    const res = '720p'

    if (!videoUrl) {
        document.getElementById('status').innerText = 'Ошибка: Введите URL видео';
        return;
    }

    document.getElementById('status').innerText = 'Загрузка...';
    document.getElementById('progressBar').value = 0; // Сбрасываем прогресс

    // Вызываем функцию downloadVideo из Python через API
    pywebview.api.downloadVideo(videoUrl, res).then(function(response) {
        document.getElementById('status').innerText = response;
        document.getElementById('progressBar').value = 0; // Сбрасываем прогресс после завершения
    });
});

// Функция для обновления прогресса
window.updateProgress = function(progress) {
    document.getElementById('progressBar').value = progress;
};