// Добавляем обработчик события для кнопки "Добавить в очередь"
document.getElementById('addBtn').addEventListener('click', function() {
    const videoUrl = document.getElementById('videoUrl').value;
    const selectedFormat = document.getElementById('format').value; // Получаем выбранный формат
    const selectedResolution = document.getElementById('resolution').value; // Получаем выбранное разрешение

    if (!videoUrl) {
        document.getElementById('status').innerText = 'Ошибка: Введите URL видео';
        return;
    }

    // Вызываем функцию addVideoToQueue из Python через API и передаем выбранный формат
    pywebview.api.addVideoToQueue(videoUrl, selectedFormat, selectedResolution).then(function(response) {
        document.getElementById('status').innerText = response;
    });
});

// Добавляем обработчик события для кнопки "Начать загрузку"
document.getElementById('startBtn').addEventListener('click', function() {
    // Вызываем функцию startDownload из Python через API
    pywebview.api.startDownload().then(function(response) {
        document.getElementById('status').innerText = response;
    });
});

// Функция для добавления видео в список
window.addVideoToList = function(videoTitle) {
    const queueList = document.getElementById('queue');
    const listItem = document.createElement('li');
    listItem.innerText = videoTitle;
    queueList.appendChild(listItem);
};

// Функция для удаления видео из списка
window.removeVideoFromList = function(videoTitle) {
    const queueList = document.getElementById('queue');
    const items = queueList.getElementsByTagName('li');
    for (let i = 0; i < items.length; i++) {
        if (items[i].innerText === videoTitle) {
            queueList.removeChild(items[i]);
            break;
        }
    }
};