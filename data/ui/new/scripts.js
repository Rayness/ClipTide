// Инициализация приложения
document.addEventListener("DOMContentLoaded", function() {
    // Проверка API pywebview
    if (window.pywebview) {
        initPyWebViewHandlers();
    } else {
        console.warn("pywebview API not available");
        mockPyWebViewAPI();
    }
    
    initEventHandlers();
    setupUIEffects();
});

function initPyWebViewHandlers() {
    window.pywebview.api.updateStatus = function(status) {
        showNotification(status);
    };
    
    window.pywebview.api.updateQueue = function(queue) {
        updateQueueList(queue);
    };
    
    window.pywebview.api.updateTaskProgress = function(taskId, progress, speed) {
        updateTaskProgress(taskId, progress, speed);
    };
    
    window.pywebview.api.updateTaskStatus = function(taskId, status) {
        updateTaskStatus(taskId, status);
    };
}

function mockPyWebViewAPI() {
    window.pywebview = {
        api: {
            addVideoToQueue: function(url, format, resolution) {
                return new Promise(resolve => {
                    setTimeout(() => {
                        const taskId = `mock_${Date.now()}`;
                        const mockResponse = `Added to queue: ${url}`;
                        resolve(mockResponse);
                        
                        const mockTask = {
                            id: taskId,
                            title: `Mock Video ${Math.floor(Math.random() * 1000)}`,
                            format: format,
                            resolution: resolution,
                            thumbnail: 'https://via.placeholder.com/120x90',
                            status: 'queued',
                            progress: 0,
                            speed: '0 KB/s'
                        };
                        
                        addTaskToList(mockTask);
                    }, 500);
                });
            },
            startDownload: function() {
                return new Promise(resolve => {
                    setTimeout(() => {
                        resolve("Download started");
                        mockDownloadProgress();
                    }, 500);
                });
            },
            removeVideoFromQueue: function(taskId) {
                return new Promise(resolve => {
                    setTimeout(() => {
                        resolve(true);
                        removeTaskFromList(taskId);
                    }, 300);
                });
            },
            cancelDownload: function(taskId) {
                return new Promise(resolve => {
                    setTimeout(() => {
                        resolve(true);
                        updateTaskStatus(taskId, 'cancelled');
                    }, 300);
                });
            }
        }
    };
}

function initEventHandlers() {
    // Добавление видео в очередь
    document.getElementById('addToQueue').addEventListener('click', function() {
        const videoUrl = document.getElementById('videoUrl').value;
        const format = document.getElementById('format').value;
        const resolution = document.getElementById('resolution').value;
        
        if (!videoUrl) {
            showNotification("Please enter a video URL", "error");
            return;
        }
        
        window.pywebview.api.addVideoToQueue(videoUrl, format, resolution)
            .then(response => {
                showNotification(response);
                document.getElementById('videoUrl').value = '';
            })
            .catch(error => {
                showNotification(`Error: ${error}`, "error");
            });
    });
    
    // Начало загрузки
    document.getElementById('startDownload').addEventListener('click', function() {
        window.pywebview.api.startDownload()
            .then(response => {
                showNotification(response);
            })
            .catch(error => {
                showNotification(`Error: ${error}`, "error");
            });
    });
    
    // Отмена всех загрузок
    document.getElementById('cancelAll').addEventListener('click', function() {
        if (confirm("Are you sure you want to cancel all downloads?")) {
            document.querySelectorAll('.queue-item').forEach(item => {
                const taskId = item.dataset.taskId;
                if (item.querySelector('.status-downloading')) {
                    window.pywebview.api.cancelDownload(taskId);
                }
            });
        }
    });
    
    // Очистка очереди
    document.getElementById('clearQueue').addEventListener('click', function() {
        if (confirm("Are you sure you want to clear the queue?")) {
            document.querySelectorAll('.queue-item').forEach(item => {
                const taskId = item.dataset.taskId;
                if (!item.querySelector('.status-downloading')) {
                    window.pywebview.api.removeVideoFromQueue(taskId);
                }
            });
        }
    });
    
    // Открытие модального окна очереди
    document.querySelector('[data-section="queue"]').addEventListener('click', openQueueModal);
    
    // Закрытие модального окна
    document.querySelector('.close-modal').addEventListener('click', closeModal);
}

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
            title: task[2],
            format: task[3],
            resolution: task[4],
            thumbnail: task[5],
            status: 'queued',
            progress: 0,
            speed: '0 KB/s'
        });
    });
}

function addTaskToList(task) {
    const queueList = document.getElementById('queueItems');
    const listItem = document.createElement('li');
    listItem.className = 'queue-item';
    listItem.dataset.taskId = task.id;
    
    listItem.innerHTML = `
        <img src="${task.thumbnail}" alt="Thumbnail" class="queue-item-thumbnail">
        <div class="queue-item-info">
            <h4>${task.title}</h4>
            <div class="queue-item-details">
                <span>${task.format.toUpperCase()}</span>
                <span>•</span>
                <span>${task.resolution}p</span>
                <span>•</span>
                <span class="queue-item-speed">${task.speed}</span>
            </div>
            <div class="queue-item-status">
                <span class="status-badge status-${task.status}">
                    ${getStatusText(task.status)}
                </span>
            </div>
            <div class="progress-container">
                <div class="progress-bar" style="width: ${task.progress}%"></div>
            </div>
        </div>
        <div class="queue-item-actions">
            <button class="cancel-btn" data-task-id="${task.id}">
                <i class="fas fa-times"></i>
            </button>
            <button class="remove-btn" data-task-id="${task.id}">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    
    queueList.appendChild(listItem);
    
    // Добавляем обработчики для кнопок
    listItem.querySelector('.cancel-btn').addEventListener('click', function() {
        const taskId = this.dataset.taskId;
        window.pywebview.api.cancelDownload(taskId);
    });
    
    listItem.querySelector('.remove-btn').addEventListener('click', function() {
        const taskId = this.dataset.taskId;
        window.pywebview.api.removeVideoFromQueue(taskId);
    });
}

function updateTaskProgress(taskId, progress, speed) {
    const taskElement = document.querySelector(`.queue-item[data-task-id="${taskId}"]`);
    if (taskElement) {
        taskElement.querySelector('.progress-bar').style.width = `${progress}%`;
        taskElement.querySelector('.queue-item-speed').textContent = speed;
    }
}

function updateTaskStatus(taskId, status) {
    const taskElement = document.querySelector(`.queue-item[data-task-id="${taskId}"]`);
    if (taskElement) {
        // Обновляем статус
        const statusBadge = taskElement.querySelector('.status-badge');
        statusBadge.className = `status-badge status-${status}`;
        statusBadge.textContent = getStatusText(status);
        
        // Обновляем активные загрузки
        updateActiveDownloadsCount();
    }
}

function removeTaskFromList(taskId) {
    const taskElement = document.querySelector(`.queue-item[data-task-id="${taskId}"]`);
    if (taskElement) {
        taskElement.remove();
        updateActiveDownloadsCount();
    }
}

function getStatusText(status) {
    const statusTexts = {
        'queued': 'Queued',
        'downloading': 'Downloading',
        'completed': 'Completed',
        'error': 'Error',
        'cancelled': 'Cancelled'
    };
    return statusTexts[status] || status;
}

function updateActiveDownloadsCount() {
    const activeCount = document.querySelectorAll('.status-downloading').length;
    document.getElementById('activeDownloads').textContent = activeCount;
}

function openQueueModal() {
    document.getElementById('queueModal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
    updateActiveDownloadsCount();
}

function closeModal() {
    document.getElementById('queueModal').style.display = 'none';
    document.body.style.overflow = '';
}

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

function mockDownloadProgress() {
    const tasks = document.querySelectorAll('.queue-item .status-queued');
    tasks.forEach((task, index) => {
        setTimeout(() => {
            const taskId = task.closest('.queue-item').dataset.taskId;
            updateTaskStatus(taskId, 'downloading');
            
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 5;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(interval);
                    updateTaskStatus(taskId, 'completed');
                    showNotification('Download completed!', 'success');
                }
                updateTaskProgress(taskId, progress, `${(Math.random() * 5).toFixed(2)} MB/s`);
            }, 500);
        }, index * 1500);
    });
}

// Экспортируем функции для использования в pywebview
window.updateQueue = updateQueueList;
window.updateTaskProgress = updateTaskProgress;
window.updateTaskStatus = updateTaskStatus;
window.removeTaskFromList = removeTaskFromList;