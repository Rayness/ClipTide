function loadNotifications(data) {
    const container = document.getElementById("notification-container");
    container.innerHTML = "";
    
    notifs = data
    notifs.reverse().forEach(n => {
    if (n.read != "True") {
        const block = document.createElement("div");
        let icon = "";

        console.log("Уведомление создано!")

        block.className = "block";
        block.id = "notif-" + n.id;

        
            if (n.type == "local") {
                if (n.source == "downloader") {
                    icon = '<i class="fa-solid fa-download"></i>';
                    console.log("Загрузчик");
                } 
                if (n.source == "donverter") {
                    icon = '<i class="fa-solid fa-download"></i>';
                    console.log("Конвертер");
                }
            } else {
                icon = 'Сервер';
            }
            
            block.innerHTML = `
            <div class="icon">
                ${icon}
            </div>
            <div class="body">
                <h4>${n.title}</h4>
                <p>${n.message}</p>
                <div class="datetime">
                    <p>${n.timestamp}</p>
                </div>
            </div>
            <div class="remove">
                <button class="delete-notif-btn">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                    <path
                        d="M64 32C28.7 32 0 60.7 0 96L0 416c0 35.3 28.7 64 64 64l384 0c35.3 0 64-28.7 64-64l0-320c0-35.3-28.7-64-64-64L64 32zM175 175c9.4-9.4 24.6-9.4 33.9 0l47 47 47-47c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9l-47 47 47 47c9.4 9.4 9.4 24.6 0 33.9s-24.6 9.4-33.9 0l-47-47-47 47c-9.4 9.4-24.6 9.4-33.9 0s-9.4-24.6 0-33.9l47-47-47-47c-9.4-9.4-9.4-24.6 0-33.9z"
                        />
                    </svg>
                </button>
            </div>
            `;
            container.appendChild(block);
            
            button = block.querySelector(".delete-notif-btn")
            button.addEventListener("click", () => {
                console.log(n.id);
                mark_notification_as_read(n.id);
            })
        }
    });
}

function mark_notification_as_read(id) {
    const cont = document.getElementById("notification-container");
    const item = cont.querySelector(`#notif-${id}`);

    console.log(id)
    if (item) {
        cont.removeChild(item);
    }
    window.pywebview.api.mark_notification_as_read(id);
}

function load_settingsNotificatios(video, conversion) {
    const switch_down = document.getElementById('switch_notifiDownload');
    const switch_conv = document.getElementById('switch_notifiConvertion');

    if (video == "True") {
        switch_down.checked = true
    } else {
        switch_down.checked = false
    };

    if (conversion == "True") {
        switch_conv.checked = true
    } else {
        switch_conv.checked = false
    }
    
}

document.getElementById('switch_notifiDownload').addEventListener('change', () => {
    const checkbox = document.getElementById('switch_notifiDownload');
    
    if (checkbox.checked) {
        window.pywebview.api.switch_notifi("downloads", "True")
    } else {
        window.pywebview.api.switch_notifi("downloads", "False")
    }
})

document.getElementById('switch_notifiConvertion').addEventListener('change', () => {
    const checkbox = document.getElementById('switch_notifiConvertion');
    
    if (checkbox.checked) {
        window.pywebview.api.switch_notifi("conversion", "True")
    } else {
        window.pywebview.api.switch_notifi("conversion", "False")
    }
})