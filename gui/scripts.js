 // Добавляем обработчик события для кнопки
 document.getElementById('downloadBtn').addEventListener('click', function() {
    const videoUrl = document.getElementById('videoUrl').value;

    if (!videoUrl) {
        document.getElementById('status').innerText = 'Ошибка: Введите URL видео';
        return;
    }

    document.getElementById('status').innerText = 'Загрузка...';

    // Вызываем функцию downloadVideo из Python через API
    pywebview.api.downloadVideo(videoUrl).then(function(response) {
        document.getElementById('status').innerText = response;
    });
});