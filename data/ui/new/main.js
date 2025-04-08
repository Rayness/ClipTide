// main.js
document.addEventListener("DOMContentLoaded", function() {
    // Инициализация приложения
    if (window.pywebview) {
        initPyWebViewHandlers();
    } else {
        console.warn("pywebview API not available");
        mockPyWebViewAPI();
    }
    
    initEventHandlers();
    setupUIEffects();
    loadInitialData();
});

// Загрузка начальных данных
function loadInitialData() {
    if (window.pywebview) {
        window.pywebview.api.get_queue().then(queue => {
            updateQueueList(queue);
        });
    }
}

// Инициализация обработчиков pywebview
function initPyWebViewHandlers() {
    window.pywebview.api.updateStatus = function(status) {
        showNotification(status);
    };
    
    window.pywebview.api.updateQueue = function(queue) {
        updateQueueList(queue);
    };
    
    window.pywebview.api.updateTaskProgress = function(taskId, progress, speed, eta) {
        updateTaskProgress(taskId, progress, speed, eta);
    };
    
    window.pywebview.api.updateTaskStatus = function(taskId, status) {
        updateTaskStatus(taskId, status);
    };
}

// Мок API для тестирования без pywebview
function mockPyWebViewAPI() {
    window.pywebview = {
        api: {
            get_video_info: function(url) {
                return new Promise(resolve => {
                    setTimeout(() => {
                        resolve({
                            title: "Mock Video",
                            thumbnail: "https://via.placeholder.com/120x90",
                            formats: ["mp4", "mkv"],
                            resolutions: [1080, 720, 480],
                            has_audio_only: true,
                            extractor: "youtube"
                        });
                    }, 500);
                });
            },
            
            add_to_queue: function(url, format, resolution, downloadThumbnail, downloadSubtitles) {
                return new Promise(resolve => {
                    setTimeout(() => {
                        const taskId = `mock_${Date.now()}`;
                        resolve([true, `Added to queue: ${url}`]);
                        
                        const mockTask = {
                            id: taskId,
                            title: `Mock Video ${Math.floor(Math.random() * 1000)}`,
                            extractor: "youtube",
                            format: format,
                            resolution: resolution,
                            thumbnail: 'https://via.placeholder.com/120x90',
                            status: 'queued',
                            progress: 0,
                            speed: '0 KB/s',
                            eta: '--:--'
                        };
                        
                        addTaskToList(mockTask);
                    }, 500);
                });
            },
            
            start_download: function(taskId) {
                return new Promise(resolve => {
                    setTimeout(() => {
                        resolve("Download started");
                        if (taskId) {
                            updateTaskStatus(taskId, 'downloading');
                            mockDownloadProgress(taskId);
                        } else {
                            mockDownloadAll();
                        }
                    }, 500);
                });
            },
            
            pause_download: function(taskId) {
                return new Promise(resolve => {
                    setTimeout(() => {
                        resolve(true);
                        updateTaskStatus(taskId, 'paused');
                    }, 300);
                });
            },
            
            cancel_download: function(taskId) {
                return new Promise(resolve => {
                    setTimeout(() => {
                        resolve(true);
                        removeTaskFromList(taskId);
                    }, 300);
                });
            },
            
            clear_queue: function() {
                return new Promise(resolve => {
                    setTimeout(() => {
                        resolve(true);
                        document.getElementById('queueItems').innerHTML = '';
                    }, 300);
                });
            },
            
            cancel_all_downloads: function() {
                return new Promise(resolve => {
                    setTimeout(() => {
                        resolve(true);
                        document.querySelectorAll('.queue-item').forEach(item => {
                            const taskId = item.dataset.taskId;
                            removeTaskFromList(taskId);
                        });
                    }, 300);
                });
            },
            
            set_download_folder: function(folderPath) {
                return new Promise(resolve => {
                    setTimeout(() => {
                        resolve(true);
                        showNotification(`Download folder set to: ${folderPath}`);
                    }, 300);
                });
            },
            
            set_language: function(language) {
                return new Promise(resolve => {
                    setTimeout(() => {
                        resolve(true);
                        location.reload();
                    }, 300);
                });
            },
            
            get_queue: function() {
                return new Promise(resolve => {
                    setTimeout(() => {
                        resolve([]);
                    }, 300);
                });
            }
        }
    };
}

// Инициализация обработчиков событий
function initEventHandlers() {
    // Добавление видео в очередь
    document.getElementById('addToQueue').addEventListener('click', function() {
        const videoUrl = document.getElementById('videoUrl').value;
        const format = document.getElementById('format').value;
        const resolution = document.getElementById('resolution').value;
        const downloadThumbnail = document.getElementById('downloadThumbnail').checked;
        const downloadSubtitles = document.getElementById('downloadSubtitles')?.checked || false;
        
        if (!videoUrl) {
            showNotification("Please enter a video URL", "error");
            return;
        }
        
        window.pywebview.api.add_to_queue(videoUrl, format, resolution, downloadThumbnail, downloadSubtitles)
            .then(([success, message]) => {
                showNotification(message);
                if (success) {
                    document.getElementById('videoUrl').value = '';
                    window.pywebview.api.get_queue().then(queue => {
                        updateQueueList(queue);
                    });
                }
            })
            .catch(error => {
                showNotification(`Error: ${error}`, "error");
            });
    });
    
    // Скачать сразу
    document.getElementById('downloadNow').addEventListener('click', function() {
        const videoUrl = document.getElementById('videoUrl').value;
        const format = document.getElementById('format').value;
        const resolution = document.getElementById('resolution').value;
        const downloadThumbnail = document.getElementById('downloadThumbnail').checked;
        const downloadSubtitles = document.getElementById('downloadSubtitles')?.checked || false;
        
        if (!videoUrl) {
            showNotification("Please enter a video URL", "error");
            return;
        }
        
        window.pywebview.api.add_to_queue(videoUrl, format, resolution, downloadThumbnail, downloadSubtitles)
            .then(([success, message]) => {
                showNotification(message);
                if (success) {
                    document.getElementById('videoUrl').value = '';
                    window.pywebview.api.get_queue().then(queue => {
                        updateQueueList(queue);
                        // Начать загрузку сразу
                        window.pywebview.api.start_download();
                    });
                }
            })
            .catch(error => {
                showNotification(`Error: ${error}`, "error");
            });
    });
    
    // Начать загрузку
    document.getElementById('startDownload').addEventListener('click', function() {
        window.pywebview.api.start_download()
            .then(response => {
                showNotification(response);
            })
            .catch(error => {
                showNotification(`Error: ${error}`, "error");
            });
    });
    
    // Пауза загрузки
    document.getElementById('pauseDownload').addEventListener('click', function() {
        const activeItem = document.querySelector('.queue-item .status-downloading');
        if (activeItem) {
            const taskId = activeItem.closest('.queue-item').dataset.taskId;
            window.pywebview.api.pause_download(taskId)
                .then(response => {
                    showNotification("Download paused");
                })
                .catch(error => {
                    showNotification(`Error: ${error}`, "error");
                });
        } else {
            showNotification("No active downloads to pause", "info");
        }
    });
    
    // Отмена всех загрузок
    document.getElementById('cancelAll').addEventListener('click', function() {
        if (confirm("Are you sure you want to cancel all downloads?")) {
            window.pywebview.api.cancel_all_downloads()
                .then(response => {
                    showNotification("All downloads cancelled");
                })
                .catch(error => {
                    showNotification(`Error: ${error}`, "error");
                });
        }
    });
    
    // Очистка очереди
    document.getElementById('clearQueue').addEventListener('click', function() {
        if (confirm("Are you sure you want to clear the queue?")) {
            window.pywebview.api.clear_queue()
                .then(response => {
                    showNotification("Queue cleared");
                })
                .catch(error => {
                    showNotification(`Error: ${error}`, "error");
                });
        }
    });
    
    // Изменение папки загрузки
    document.getElementById('changeFolder')?.addEventListener('click', function() {
        if (window.pywebview) {
            window.pywebview.api.set_download_folder()
                .then(success => {
                    if (success) {
                        showNotification("Download folder changed");
                    }
                })
                .catch(error => {
                    showNotification(`Error: ${error}`, "error");
                });
        }
    });
    
    // Смена языка
    document.getElementById('language')?.addEventListener('change', function() {
        const language = this.value;
        window.pywebview.api.set_language(language)
            .catch(error => {
                showNotification(`Error changing language: ${error}`, "error");
            });
    });
    
    // Открытие модального окна очереди
    document.querySelector('[data-section="queue"]').addEventListener('click', openQueueModal);
    
    // Закрытие модального окна
    document.querySelector('.close-modal').addEventListener('click', closeModal);
}

// Настройка UI эффектов
function setupUIEffects() {
    // Переключение между секциями
    document.querySelectorAll('.nav-btn').forEach(button => {
        button.addEventListener('click', function() {
            const sectionId = this.getAttribute('data-section');
            
            if (sectionId === 'queue') {
                openQueueModal();
                return;
            }
            
            document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.content-section').forEach(section => {
                section.classList.remove('active');
            });
            
            this.classList.add('active');
            document.getElementById(sectionId).classList.add('active');
        });
    });
    
    // Эффекты при наведении на кнопки
    document.querySelectorAll('.btn, .control-btn, .icon-btn').forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

// Обновление списка очереди
function updateQueueList(queue) {
    const queueList = document.getElementById('queueItems');
    queueList.innerHTML = '';
    
    if (queue.length === 0) {
        queueList.innerHTML = '<li class="empty-queue">Queue is empty</li>';
        return;
    }
    
    queue.forEach(task => {
        addTaskToList({
            id: task[0],
            title: task[1],
            extractor: task[2],
            format: task[3],
            resolution: task[4],
            thumbnail: task[5],
            status: task[6],
            progress: task[7],
            speed: task[8],
            eta: task[9]
        });
    });
    
    updateActiveDownloadsCount();
}

// Добавление задачи в список
// Обновленная функция addTaskToList
function addTaskToList(taskData) {
    const queueList = document.getElementById('queueItems');
    const emptyItem = queueList.querySelector('.empty-queue');
    if (emptyItem) {
        emptyItem.remove();
    }

    const listItem = document.createElement('li');
    listItem.className = 'queue-item';
    listItem.dataset.taskId = taskData.id;
    
    // Экранируем специальные символы в названии
    const safeTitle = escapeHtml(taskData.title);
    const safeThumbnail = taskData.thumbnail || 'https://via.placeholder.com/120x90';
    
    listItem.innerHTML = `
        <div class="queue-item-loading">
            <div class="loading-spinner"></div>
        </div>
        <img src="${safeThumbnail}" alt="Thumbnail" class="queue-item-thumbnail">
        <div class="queue-item-info">
            <h4>${safeTitle}</h4>
            <div class="queue-item-details">
                <span class="queue-item-service">${taskData.extractor}</span>
                <span>•</span>
                <span>${taskData.format.toUpperCase()}</span>
                <span>•</span>
                <span>${taskData.resolution}p</span>
                <span>•</span>
                <span class="queue-item-speed">${taskData.speed}</span>
                <span>•</span>
                <span class="queue-item-eta">${taskData.eta}</span>
            </div>
            <div class="queue-item-status">
                <span class="status-badge status-${taskData.status}">
                    ${getStatusText(taskData.status)}
                </span>
            </div>
            <div class="progress-container">
                <div class="progress-bar" style="width: ${taskData.progress}%" data-progress="${taskData.progress}"></div>
                <div class="progress-text">${taskData.progress}%</div>
            </div>
        </div>
        <div class="queue-item-actions">
            <button class="action-btn start-btn" data-task-id="${taskData.id}" ${taskData.status !== 'queued' ? 'disabled' : ''}>
                <i class="fas fa-play"></i>
            </button>
            <button class="action-btn pause-btn" data-task-id="${taskData.id}" ${taskData.status !== 'downloading' ? 'disabled' : ''}>
                <i class="fas fa-pause"></i>
            </button>
            <button class="action-btn cancel-btn" data-task-id="${taskData.id}">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    queueList.appendChild(listItem);
    
    // Показываем анимацию загрузки на 2 секунды
    const loadingSpinner = listItem.querySelector('.queue-item-loading');
    setTimeout(() => {
        loadingSpinner.style.opacity = '0';
        setTimeout(() => {
            loadingSpinner.remove();
        }, 500);
    }, 2000);

    // Добавляем обработчики для кнопок
    listItem.querySelector('.start-btn').addEventListener('click', function() {
        const taskId = this.dataset.taskId;
        window.pywebview.api.start_download(taskId);
    });
    
    listItem.querySelector('.pause-btn').addEventListener('click', function() {
        const taskId = this.dataset.taskId;
        window.pywebview.api.pause_download(taskId);
    });
    
    listItem.querySelector('.cancel-btn').addEventListener('click', function() {
        const taskId = this.dataset.taskId;
        window.pywebview.api.cancel_download(taskId);
    });
    
    updateActiveDownloadsCount();
}

// Функция для экранирования HTML-символов
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Обновление прогресса задачи
// Обновленная функция updateTaskProgress
function updateTaskProgress(taskId, progress, speed, eta) {
    const taskElement = document.querySelector(`.queue-item[data-task-id="${taskId}"]`);
    if (taskElement) {
        const progressBar = taskElement.querySelector('.progress-bar');
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('data-progress', progress);
        
        taskElement.querySelector('.queue-item-speed').textContent = speed;
        taskElement.querySelector('.queue-item-eta').textContent = eta;
        
        // Анимация заполнения прогресс-бара
        progressBar.style.transition = 'width 0.5s ease';
    }
}

// Обновление статуса задачи
function updateTaskStatus(taskId, status) {
    const taskElement = document.querySelector(`.queue-item[data-task-id="${taskId}"]`);
    if (taskElement) {
        // Обновляем статус
        const statusBadge = taskElement.querySelector('.status-badge');
        statusBadge.className = `status-badge status-${status}`;
        statusBadge.textContent = getStatusText(status);
        
        // Обновляем кнопки
        const startBtn = taskElement.querySelector('.start-btn');
        const pauseBtn = taskElement.querySelector('.pause-btn');
        
        startBtn.disabled = status !== 'queued';
        pauseBtn.disabled = status !== 'downloading';
        
        // Обновляем активные загрузки
        updateActiveDownloadsCount();
    }
}

// Удаление задачи из списка
function removeTaskFromList(taskId) {
    const taskElement = document.querySelector(`.queue-item[data-task-id="${taskId}"]`);
    if (taskElement) {
        taskElement.remove();
        updateActiveDownloadsCount();
        
        // Если очередь пуста, показываем сообщение
        const queueList = document.getElementById('queueItems');
        if (queueList.children.length === 0) {
            queueList.innerHTML = '<li class="empty-queue">Queue is empty</li>';
        }
    }
}

// Получение текста статуса
function getStatusText(status) {
    const statusTexts = {
        'queued': 'Queued',
        'downloading': 'Downloading',
        'completed': 'Completed',
        'error': 'Error',
        'paused': 'Paused',
        'cancelled': 'Cancelled'
    };
    return statusTexts[status] || status;
}

// Обновление счетчика активных загрузок
function updateActiveDownloadsCount() {
    const activeCount = document.querySelectorAll('.status-downloading').length;
    document.getElementById('activeDownloads').textContent = activeCount;
    
    // Обновляем бейдж на иконке загрузки
    const downloadBadge = document.querySelector('.download-controls .badge');
    if (downloadBadge) {
        downloadBadge.textContent = activeCount;
        downloadBadge.style.display = activeCount > 0 ? 'flex' : 'none';
    }
}

// Открытие модального окна очереди
function openQueueModal() {
    document.getElementById('queueModal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
    updateActiveDownloadsCount();
}

// Закрытие модального окна
function closeModal() {
    document.getElementById('queueModal').style.display = 'none';
    document.body.style.overflow = '';
}

// Показать уведомление
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Мок прогресса загрузки для тестирования
function mockDownloadProgress(taskId) {
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 5;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
            updateTaskStatus(taskId, 'completed');
            showNotification('Download completed!', 'success');
        }
        updateTaskProgress(taskId, progress, `${(Math.random() * 5).toFixed(2)} MB/s`, '00:30');
    }, 500);
}

function mockDownloadAll() {
    const tasks = document.querySelectorAll('.queue-item .status-queued');
    tasks.forEach((task, index) => {
        setTimeout(() => {
            const taskId = task.closest('.queue-item').dataset.taskId;
            updateTaskStatus(taskId, 'downloading');
            mockDownloadProgress(taskId);
        }, index * 1500);
    });
}

// Экспортируем функции для использования в pywebview
window.updateQueue = updateQueueList;
window.updateTaskProgress = updateTaskProgress;
window.updateTaskStatus = updateTaskStatus;
window.removeTaskFromList = removeTaskFromList;
window.showNotification = showNotification;