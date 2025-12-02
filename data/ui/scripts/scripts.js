//  Copyright (C) 2025 Rayness
//  This program is free software under GPLv3. See LICENSE for details.

// --- Инициализация и Вкладки ---
document.addEventListener('DOMContentLoaded', function() {
    window.isDomReady = true;
    const buttons = document.querySelectorAll('.tab-btn');
    const blocks = document.querySelectorAll('.content');
    const name = document.getElementById('name');
    
    const stopBtnConv = document.getElementById("stopBtn_conv");
    if(stopBtnConv) stopBtnConv.disabled = true;
    
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            buttons.forEach(btn => btn.classList.remove('active'));
            blocks.forEach(block => block.classList.remove('active'));
            
            this.classList.add('active');
            
            const tabId = this.getAttribute('data-tab');
            const block = document.getElementById(tabId)
            if(block) {
                block.classList.add('active');
                if(name) name.textContent = block.getAttribute('data-status');
            }
        });
    });
    
    if(buttons.length > 0) buttons[0].click();
});

// --- Drag & Drop и Выбор файлов ---
const dropArea = document.getElementById('dropZone');
if (dropArea) {
    dropArea.addEventListener('click', () => {
        window.pywebview.api.openFile();
    });
}

document.getElementById("close-video").addEventListener('click', closeVideo);

function closeVideo() {
    document.getElementById('input-file').style.display = 'grid'; // Вернул grid, как было в стилях обычно
    document.getElementById('main-app').style.display = 'none';
}

// Эту функцию вызывает Python (Converter)
window.file_is_input = function(data) {
    document.getElementById('input-file').style.display = 'none';
    document.getElementById('main-app').style.display = 'block';

    if (data.error) {
        console.error('Error:', data.error);
        document.getElementById('status').innerText = data.error;
        return;
    }

    // Заполняем данными
    if(document.getElementById('conv_name')) document.getElementById('conv_name').textContent = data.file_name;
    if(document.getElementById('conv_duration')) document.getElementById('conv_duration').textContent = formatDuration(data.duration);
    if(document.getElementById('conv_bit_rate-video')) document.getElementById('conv_bit_rate-video').textContent = `${data.bitrate} kbps`;
    if(document.getElementById('conv_bit_rate-audio')) document.getElementById('conv_bit_rate-audio').textContent = `${data.audio_bitrate} kbps`;
    if(document.getElementById('conv_framerate')) document.getElementById('conv_framerate').textContent = `${data.fps} fps`;
    if(document.getElementById('conv_video_codec')) document.getElementById('conv_video_codec').textContent = data.codec;
    if(document.getElementById('conv_audio_codec')) document.getElementById('conv_audio_codec').textContent = data.audio_codec;

    if (data.thumbnail) {
        document.getElementById('conv_image').src = data.thumbnail;
    }

    hideSpinner();
}

// --- Downloader Logic ---

// Кнопка "Добавить в очередь"
document.getElementById('addBtn').addEventListener('click', function() {
    const videoUrl = document.getElementById('videoUrl').value;
    const selectedFormat = document.getElementById('format').value;
    const selectedResolution = document.getElementById('resolution').value;

    if (!videoUrl) {
        // Тут можно взять перевод из переменной, но пока так
        document.getElementById('status').innerText = 'Error: Enter URL'; 
        return;
    }

    showSpinner();

    // Вызываем Python
    window.pywebview.api.addVideoToQueue(videoUrl, selectedFormat, selectedResolution)
        .catch(() => {
            document.getElementById('status').innerHTML = 'API Error';
            hideSpinner();
        });
        
    document.getElementById('videoUrl').value = '';
});

// Кнопка "Начать загрузку"
document.getElementById('startBtn').addEventListener('click', function() {
    window.pywebview.api.startDownload();
});

// Кнопка "Остановить загрузку"
document.getElementById("stopBtn").addEventListener('click', function() {
    window.pywebview.api.stopDownload();
})

// Управление форматами (блокировка разрешения для mp3)
document.getElementById('format').addEventListener('change', ()=> {
    const element = document.getElementById('format');
    const res = document.getElementById('resolution');

    if (element.value === 'mp3') {
        res.selectedIndex = -1;
        res.disabled = true;
    } else {
        res.disabled = false;
        res.selectedIndex = 4; // Default 1080p?
    }
})

// --- UI Helpers (Вызываются из Python) ---

window.showSpinner = function() {
    const spinner = document.getElementById('loading-spinner');
    if(spinner) spinner.style.display = 'block';
    
    toggleButtons(true);
}

window.hideSpinner = function() {
    const spinner = document.getElementById('loading-spinner');
    if(spinner) spinner.style.display = 'none'; 
    
    toggleButtons(false);
}

function toggleButtons(disabled) {
    const ids = ['addBtn', 'startBtn', 'convert_btn'];
    ids.forEach(id => {
        const btn = document.getElementById(id);
        if(btn) btn.disabled = disabled;
    });
}

// Универсальная функция обновления прогресса (для Python)
window.updateProgressBar = function(progress, speed, eta) {
    // Прогресс
    if (progress !== undefined && progress !== "") {
        const pText = document.getElementById("progress");
        const pFill = document.getElementById("progress-fill");
        // Пытаемся сохранить префикс "Progress" если он есть в тексте, или просто число
        // Но лучше, чтобы Python просто слал числа, а JS добавлял текст.
        // Сейчас Python шлет вызовы updateProgressBar(50, "2 MB/s", "1 min")
        
        // Для упрощения, предположим, что мы просто обновляем цифры, 
        // а слова "Speed", "ETA" уже есть в span или добавляются тут.
        // В твоем коде Python в downloader.py сам формирует строки "Speed: ...".
        
        // Если Python прислал просто число:
        if (typeof progress === 'number') {
             if(pText) pText.innerText = `Progress ${progress}%`;
             if(pFill) pFill.style.width = `${progress}%`;
        }
    }

    // Скорость (если передана строка уже с единицами)
    if (speed) {
        const sEl = document.getElementById("speed");
        if(sEl) sEl.innerText = speed.includes("Speed") ? speed : `Speed ${speed}`;
    }

    // ETA
    if (eta) {
        const eEl = document.getElementById("eta");
        if(eEl) eEl.innerText = eta.includes("ETA") ? eta : `ETA ${eta}`;
    }
}

// --- Очередь (Queue) ---

// Функция принимает объект videoData из Python
window.addVideoToList = function(videoData) {
    const queueList = document.getElementById("queue");
    // Проверка на дубликаты (если вдруг)
    if(document.getElementById(`item-${videoData.id}`)) return;

    const listItem = document.createElement("li");
    listItem.id = `item-${videoData.id}`; // Уникальный ID DOM элемента

    // Генерируем HTML внутри элемента
    const thumb = videoData.thumbnail || "src/default_thumbnail.png";
    const details = videoData.format === "mp3" 
        ? `Audio / ${videoData.format}` 
        : `${videoData.resolution}p / ${videoData.format}`;

    listItem.innerHTML = `
        <div class="queue-item-top">
            <div class="queue-item-info">
                <img src="${thumb}" alt="thumb">
                <div class="video-info">
                    <div class="video_queue_text" title="${videoData.title}">${videoData.title}</div>
                    <div class="video-details" style="margin-top: 5px;">
                        <span style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;">${details}</span>
                    </div>
                </div>
            </div>
            <button class="delete-button" onclick="window.removeVideoFromQueue('${videoData.id}')">
                <i class="fa-solid fa-xmark"></i>
            </button>
        </div>
        
        <!-- Статус бар -->
        <div class="queue-item-bottom">
            <div class="mini-progress-track">
                <div class="mini-progress-fill" id="prog-bar-${videoData.id}" style="width: 0%"></div>
            </div>
            <div class="queue-item-stats">
                <span id="status-${videoData.id}">Ожидание...</span>
                <span>
                    <span id="speed-${videoData.id}">-- MB/s</span> | 
                    <span id="eta-${videoData.id}">--:--</span>
                </span>
            </div>
        </div>
    `;

    queueList.appendChild(listItem);
}


// Загрузка очереди при старте
window.loadQueue = function(queue) {
    const queueList = document.getElementById('queue');
    if (!queueList) return;
    queueList.innerHTML = "";
    
    // Теперь queue это список словарей, а не кортежей (мы изменили это в downloader.py)
    // Но если старый файл queue.json содержит списки, надо проверить.
    
    queue.forEach(video => {
        // Проверка совместимости (если вдруг загрузили старый json)
        let vData = video;
        if (Array.isArray(video)) {
             // Конвертация старого формата [url, title, fmt, res, thumb]
             // Генерируем фейковый ID для старых записей
            vData = {
                id: "old-" + Math.random().toString(36).substr(2, 9),
                url: video[0],
                title: video[1],
                format: video[2],
                resolution: video[3],
                thumbnail: video[4]
            };
        }
        window.addVideoToList(vData);
    });
};

// Удаление
window.removeVideoFromQueue = function(taskId) {
    // Удаляем визуально
    const item = document.getElementById(`item-${taskId}`);
    if(item) item.remove();
    
    // Удаляем логически
    window.pywebview.api.removeVideoFromQueue(taskId);
}

window.removeVideoFromList = function(videoTitle) {
    const queueList = document.getElementById("queue");
    const items = queueList.getElementsByTagName("li");

    for (let i = 0; i < items.length; i++) {
        // Простая проверка на вхождение подстроки
        if (items[i].innerText.includes(videoTitle)) {
            queueList.removeChild(items[i]);
            break;
        }
    }
}

// Обновление прогресса конкретного видео
window.updateItemProgress = function(taskId, progress, speed, eta) {
    const bar = document.getElementById(`prog-bar-${taskId}`);
    const statusText = document.getElementById(`status-${taskId}`);
    const speedText = document.getElementById(`speed-${taskId}`);
    const etaText = document.getElementById(`eta-${taskId}`);

    if (bar) bar.style.width = `${progress}%`;
    if (statusText) statusText.innerText = `${progress}%`;
    if (speedText) speedText.innerText = speed;
    if (etaText) etaText.innerText = eta;
    
    // Если завершено
    if(progress >= 100) {
        if (statusText) statusText.innerText = "Готово";
        // Можно добавить анимацию исчезновения, если нужно
        // setTimeout(() => window.removeVideoFromQueue(taskId), 2000); 
    }
}


// --- Настройки и Папки (Settings) ---

window.updateDownloadFolder = function(folder_path) {
    const el = document.getElementById('folder_path');
    if(el) el.placeholder = folder_path;
}

window.updateConvertFolder = function(folder_path) {
    const el = document.getElementById('conv_folder_path');
    if(el) el.placeholder = folder_path;
}

document.getElementById("chooseButton").addEventListener("click", function() {
    window.pywebview.api.choose_folder();
});
document.getElementById("byDefoult").addEventListener("click", function() {
    window.pywebview.api.switch_download_folder();
});
document.getElementById("openFolder").addEventListener("click", () =>{
    const folder = document.getElementById('folder_path').placeholder;
    window.pywebview.api.open_folder(folder);
});

// Converter Settings
document.getElementById("chooseButton-conv").addEventListener("click", function() {
    window.pywebview.api.choose_converter_folder();
});
document.getElementById("byDefoult-conv").addEventListener("click", function() {
    window.pywebview.api.switch_converter_folder();
});
document.getElementById("openFolder-conv").addEventListener("click", () =>{
    const folder = document.getElementById('conv_folder_path').placeholder;
    window.pywebview.api.open_folder(folder);
});

// --- Converter Logic ---

document.getElementById('convert_btn').addEventListener('click', () => {
    const format = document.getElementById('conv-format').value;
    const stopBtn = document.getElementById("stopBtn_conv");
    if(stopBtn) stopBtn.disabled = false;
    
    window.pywebview.api.convert_video(format);
});

document.getElementById("stopBtn_conv").addEventListener('click', function() {
    window.pywebview.api.stop_conversion();
    this.disabled = true;
});

// --- Прочее ---

document.getElementById("update").addEventListener("click", function(){
    window.pywebview.api.launch_update();
});

document.getElementById('language').addEventListener('change', function() {
    const lang = document.getElementById('language').value || 'en'; // Исправил English на код en
    window.pywebview.api.switch_language(lang);
});

window.setLanguage = function(lang) {
    const select = document.getElementById("language");
    if (select) select.value = lang;
}

// Вспомогательная функция времени
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}


// --- Логирование ---
window.addLog = function(message) {
    const logContainer = document.getElementById("app-logs");
    if (!logContainer) return;

    const entry = document.createElement("div");
    entry.className = "log-entry";
    
    // Время
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    entry.innerText = `[${timeStr}] ${message}`;
    
    // Добавляем в начало (или конец, если flex-direction: column-reverse)
    logContainer.prepend(entry); // prepend добавляет сверху (визуально снизу из-за стилей)
}