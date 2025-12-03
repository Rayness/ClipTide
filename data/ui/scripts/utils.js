document.getElementById('switch_openDownloadFolder').addEventListener('change', function () {
    const checkbox = document.getElementById('switch_openDownloadFolder');

    if (checkbox.checked) {
      window.pywebview.api.switch_open_folder_dl("dl" ,"True");
    } else {
      window.pywebview.api.switch_open_folder_dl("dl", "False");
    }
});

document.getElementById('switch_openConverterFolder').addEventListener('change', function () {
    const checkbox = document.getElementById('switch_openConverterFolder');

    if (checkbox.checked) {
      window.pywebview.api.switch_open_folder_dl("cv" ,"True");
    } else {
      window.pywebview.api.switch_open_folder_dl("cv", "False");
    }
});

window.loadopenfolders = function(enabled_dl, enabled_cv){
  const checkbox_dl = document.getElementById('switch_openDownloadFolder');
  const checkbox_cv = document.getElementById('switch_openConverterFolder');

    if (enabled_dl == "True") {
        checkbox_dl.checked = true
    } else {
        checkbox_dl.checked = false
    };

    if (enabled_cv == "True") {
        checkbox_cv.checked = true
    } else {
        checkbox_cv.checked = false
    }
}

window.removePreloader = function() {
    const preloader = document.getElementById('app-preloader');
    if (preloader) {
        preloader.classList.add('hidden');
        
        // Удаляем из DOM через секунду, чтобы не мешал
        setTimeout(() => {
            preloader.remove();
        }, 1000);
    }
}