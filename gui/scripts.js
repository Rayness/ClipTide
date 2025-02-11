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

document.getElementById('apply').addEventListener('click', function() {
    const lang = document.getElementById('language').value;
    const folder_path = document.getElementById('folder_path').value || document.getElementById('folder_path').placeholder

    pywebview.api.switch_language(lang);
    pywebview.api.switch_download_folder(folder_path)
})

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

// Функция для обновления текста интерфейса
window.updateTranslations = function(translations) {
    document.getElementById('language_title').innerText = translations.settings.language || 'Add video';
    document.getElementById('apply').innerText = translations.settings.button_apply || 'Apply:';

    document.getElementById('videoUrl').placeholder = translations.video_URL || 'Add video';
    document.getElementById('addBtn').innerText = translations.add_to_queue || 'Add video';
    document.getElementById('startBtn').innerText = translations.start_download || 'Start download';

    document.getElementById('queue-title').innerText = translations.queue || 'Queue: ';
    document.getElementById('format_title').innerText = translations.format || 'Format: ';
    document.getElementById('resolution_title').innerText = translations.resolution || 'Resolution: ';
   
    document.getElementById('status').innerText = translations.status.status_text || 'Status. Waiting...';

    document.getElementById('progress').innerText = translations.progress + " 0% " || 'Progress: ';
    document.getElementById('speed').innerText = translations.speed + " 0 " + translations.bs || 'Speed: ';
    document.getElementById('eta').innerText = translations.eta + " 0 " + translations.min + " 0 " + translations.sec || 'Eta: ';
};

window.updateDownloadFolder = function(folder_path) {
    document.getElementById('folder_path').placeholder = folder_path;
}