updateApp = function(update, translations) {
    if (update) {
        document.getElementById('update__text').innerHTML = translations.settings.update_text_ready || 'Update ready';
        update_text.style.backgroundColor=  "#5d8a51";
    } else if (!update) {
        document.getElementById('update__text').innerHTML = translations.settings.update_text_not_ready || 'Update not required';
        update_text.style.backgroundColor = "#3e4d3a";
    } else {
        document.getElementById('update__text').innerHTML = translations.settings.update_text_error || 'Update not available';
        update_text.style.backgroundColor = "#7c363d";
    }
}


// Функция для обновления текста интерфейса
window.updateTranslations = function(translations) {
    update_text = document.getElementById('update__text')

    document.getElementById('10').setAttribute('data-status', translations.sections.setting);

    // Настройки //
    // 
    // Язык
    document.getElementById('language_settings_title').innerText = translations.settings.language.title || 'Language';
    
    document.getElementById('language_title').innerText = translations.settings.language.language || 'Language';
    document.getElementById('lang_ru').innerHTML = translations.settings.language.russian || 'Russian';
    document.getElementById('lang_en').innerHTML = translations.settings.language.english || 'English';
    document.getElementById('lang_pl').innerHTML = translations.settings.language.polish || 'Polish';
    document.getElementById('lang_ja').innerHTML = translations.settings.language.japan || 'Japan';
    document.getElementById('lang_ua').innerHTML = translations.settings.language.ukraine || 'Ukraine';
    document.getElementById('lang_de').innerHTML = translations.settings.language.german || 'German';
    document.getElementById('lang_fr').innerHTML = translations.settings.language.french || 'French';
    document.getElementById('lang_cn').innerHTML = translations.settings.language.chinese || 'Chinese';
    document.getElementById('open_locale_folder').innerHTML = translations.settings.language.open_folder || 'Open folder';


    // Оформление
    document.getElementById('decorations-title').innerHTML = translations.settings.themes.decoration || 'Decoration';
    document.getElementById('theme-title').innerHTML = translations.settings.themes.theme || 'Theme: ';
    document.getElementById('style-title').innerHTML = translations.settings.themes.style || 'Style: ';
    

    // Папки 
    document.getElementById('folders-title').innerHTML = translations.settings.folders.title || 'Folders control';

    document.getElementById('download_folder_title').innerHTML = translations.settings.folders.placeholder_download || 'Path to download folder';
    document.getElementById('conversion_folder_title').innerHTML = translations.settings.folders.placeholder_conversion || 'Path to conversion folder';

    document.getElementById('download_tooltip_defoult').innerHTML = translations.settings.folders.by_defoult || 'By default';
    document.getElementById('download_tooltip_choose').innerHTML = translations.settings.folders.choose_download_folder || 'Choose download folder';
    document.getElementById('download_tooltip_open').innerHTML = translations.settings.folders.open_download_folder || 'Open download folder';

    document.getElementById('conversion-tooltip_defoult').innerHTML = translations.settings.folders.by_defoult || 'By default';
    document.getElementById('conversion-tooltip_choose').innerHTML = translations.settings.folders.choose_converter_folder || 'Choose conversion folder';
    document.getElementById('conversion-tooltip_open').innerHTML = translations.settings.folders.open_converter_folder || 'Open conversion folder';


    // Уведомления
    document.getElementById('notification-title').innerHTML = translations.settings.notifications.title || 'Notifications conrol';
    document.getElementById('get_notifi_download').innerHTML = translations.settings.notifications.notifi_download || 'Get notifications from download';
    document.getElementById('get_notifi_conversion').innerHTML = translations.settings.notifications.notifi_conversion || 'Get notification from converter';


    // Прокси 
    document.getElementById('proxy-title').innerHTML = translations.settings.proxys.title || "Proxy-server control";
    document.getElementById('turn_on_proxy').innerHTML = translations.settings.proxys.turn_on || "Proxy-server turn on";


    // Обновления
    document.getElementById('updates-title'). innerHTML = translations.settings.updates.title || 'Updates control';
    document.getElementById('update').innerHTML = translations.settings.updates.update_button || 'Check';


    // О приложении
    document.getElementById('about-title').innerHTML = translations.settings.about.title || "About";
    document.getElementById('about-version').innerHTML = translations.settings.about.version || "Version: 1.5";
    document.getElementById('about-date').innerHTML = translations.settings.about.date || "Release: 06/11/2025";


    // Донат
    // 
    // Станица с донатом
    document.getElementById('')
    document.getElementById('donate-description').innerHTML = translations.donate.description;


    // Основной функционал //
    // 
    // Загрузка видео
    document.getElementById('videoUrl').placeholder = translations.video_URL || 'Enter video URL';
   
    // Конвертер видео
    document.getElementById('converter_add_video').innerText = translations.converter.click_for_add_video || '';

    document.getElementById('convertion-settings').innerText = translations.converter.convertion_settings || '';
    document.getElementById('convert_btn').innerText = translations.converter.conversion_button;
    document.getElementById('convertion_format').innerText = translations.converter.format;
    document.getElementById('close-video').innerText = translations.converter.close_video;
    
    document.getElementById('video_info').innerText = translations.converter.video_info.title;
    document.getElementById('conv_duration_text').innerText = translations.converter.video_info.duration;
    document.getElementById('conv_framerate_text').innerText = translations.converter.video_info.framerate;
    document.getElementById('conv_video_codec_text').innerText = translations.converter.video_info.video_codec;
    document.getElementById('conv_bit_rate-video_text').innerText = translations.converter.video_info.video_bitrate;
    document.getElementById('conv_audio_codec_text').innerText = translations.converter.video_info.audio_codec;
    document.getElementById('conv_bit_rate-audio_text').innerText = translations.converter.video_info.audio_bitrate;

    
    // Статус //
    document.getElementById('status').innerText = translations.status.status_text || 'Status. Waiting...';

    document.getElementById('progress').innerText = translations.progress + " 0% " || 'Progress: ';
    document.getElementById('speed').innerText = translations.speed + " 0 " + translations.bs || 'Speed: ';
    document.getElementById('eta').innerText = translations.eta + " 0 " + translations.min + " 0 " + translations.sec || 'Eta: ';
};