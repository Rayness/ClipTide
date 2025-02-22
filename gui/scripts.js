// Добавляем обработчик события для кнопки "Добавить в очередь"
document.getElementById('addBtn').addEventListener('click', function() {
    const videoUrl = document.getElementById('videoUrl').value;
    const selectedFormat = document.getElementById('format').value; // Получаем выбранный формат
    const selectedResolution = document.getElementById('resolution').value; // Получаем выбранное разрешение

    if (!videoUrl) {
        document.getElementById('status').innerText = 'Ошибка: Введите URL видео';
        return;
    }

    document.getElementById('status').innerText = 'Добавление в очередь...';
    showSpinner();
    document.getElementById('addBtn').disabled = true;
    document.getElementById('startBtn').disabled = true;
    

    // Вызываем функцию addVideoToQueue из Python через API и передаем выбранный формат
    pywebview.api.addVideoToQueue(videoUrl, selectedFormat, selectedResolution).then(function(response) {
        document.getElementById('status').innerText = response;
        hideSpinner();
        document.getElementById('addBtn').disabled = false;
        document.getElementById('startBtn').disabled = false;
        document.getElementById('videoUrl').value = '';
    });
});

function showSpinner() {
    document.getElementById('loading-spinner').style.display = 'block';
}

function hideSpinner() {
    document.getElementById('loading-spinner').style.display = 'none'; 
}

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
//window.addVideoToList = function(videoTitle) {
//    const queueList = document.getElementById('queue');
//    const listItem = document.createElement('li');
//    listItem.innerText = videoTitle;
//    queueList.appendChild(listItem);
//};

// Функция для добавления видео в список очереди
function addVideoToList(videoTitle, thumbnailUrl) {
    const queueList = document.getElementById("queue");
    const listItem = document.createElement("li");

    // Создаем элемент для превью
    const thumbnail = document.createElement("img");
    thumbnail.src = thumbnailUrl || "src/default_thumbnail.png"; // Если превью отсутствует, используем дефолтное изображение
    thumbnail.alt = "Превью видео";

    // Создаем контейнер для информации о видео
    const videoInfo = document.createElement("div");
    videoInfo.classList.add("video-info");
    videoInfo.innerText = videoTitle;

    // Создаем кнопку удаления
    const deleteButton = document.createElement("button");
    deleteButton.innerText = "Удалить";
    deleteButton.classList.add("delete-button");
    deleteButton.onclick = function () {
        removeVideoFromQueue(videoTitle); // Вызываем функцию для удаления видео
    };

    // Добавляем элементы в список
    listItem.appendChild(thumbnail);
    listItem.appendChild(videoInfo);
    listItem.appendChild(deleteButton);

    // Добавляем элемент в очередь
    queueList.appendChild(listItem);
}

// Функция для удаления видео из очереди
function removeVideoFromQueue(videoTitle) {
    window.pywebview.api.removeVideoFromQueue(videoTitle); // Вызываем API для удаления
}

window.loadQueue = function(queue) {
    const queueList = document.getElementById('queue');
    queueList.innerHTML = ""; // Очищаем перед загрузкой

    queue.forEach(video => {
        const listItem = document.createElement('li');

        // Создаем элемент для превью
        const thumbnail = document.createElement("img");
        thumbnail.src = video[4] || "src/default_thumbnail.png"; // Если превью отсутствует, используем дефолтное изображение
        thumbnail.alt = "Превью видео";

        // Создаем контейнер для информации о видео
        const videoInfo = document.createElement("div");
        videoInfo.classList.add("video-info");
        videoInfo.innerText = video[1];

        // Создаем кнопку удаления
        const deleteButton = document.createElement("button");
        deleteButton.innerText = "Удалить";
        deleteButton.classList.add("delete-button");
        deleteButton.onclick = function () {
            removeVideoFromQueue(video[1]); // Вызываем функцию для удаления видео
        };

        // Добавляем текст и кнопку в элемент списка
        listItem.appendChild(thumbnail);
        listItem.appendChild(videoInfo);
        listItem.appendChild(deleteButton);

        // Добавляем элемент в очередь
        queueList.appendChild(listItem);
    });
};

// Функция для удаления видео из интерфейса
function removeVideoFromList(videoTitle) {
    const queueList = document.getElementById("queue");
    const items = queueList.getElementsByTagName("li");

    for (let i = 0; i < items.length; i++) {
        if (items[i].innerText.includes(videoTitle)) {
            queueList.removeChild(items[i]);
            break;
        }
    }
}

// Функция для обновления текста интерфейса
window.updateTranslations = function(translations) {
    document.getElementById('language_title').innerText = translations.settings.language || 'Language';
    document.getElementById('folder_title').innerText = translations.settings.placeholder || 'Specify the path to the download folder';
    document.getElementById('apply').innerText = translations.settings.button_apply || 'Apply:';

    document.getElementById('lang_ru').innerHTML = translations.settings.russian || 'Russian';
    document.getElementById('lang_en').innerHTML = translations.settings.english || 'English';

    document.getElementById('videoUrl').placeholder = translations.video_URL || 'Enter video URL';
    document.getElementById('addBtn').innerText = translations.add_to_queue || 'Add video';
    document.getElementById('startBtn').innerText = translations.start_downloading || 'Start download';

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