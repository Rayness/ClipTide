[![Supported Python Versions](https://img.shields.io/badge/python-3.12%20%7C%203.13-%234B8BBE)](https://www.python.org/downloads/) [![Downloads](https://img.shields.io/github/downloads/Rayness/YouTube-Downloader/total)](https://github.com/Rayness/YouTube-Downloader/releases) [![Release date](https://img.shields.io/github/release-date/Rayness/YouTube-Downloader)]() [![Version tag](https://img.shields.io/github/v/tag/Rayness/YouTube-Downloader)]()

![YT-downloader](https://github.com/user-attachments/assets/6c9eaace-f0aa-4924-8498-bed1be55ca97)

[English Readme](https://github.com/Rayness/YouTube-Downloader/blob/main/README.md)
 • [Русский Readme](https://github.com/Rayness/YouTube-Downloader/blob/main/README.ru.md)

## Общая информация 
> [!NOTE]
> Данная небольшая программа предназначена для скачивания видео контента в аудио и видео форматах с видеохостинга YouTube, но так же поддерживаются и другие платформы, такие как: Rutube, Vkvideo, ok и многие другие. Работает всё на Python с использованием бибилиотеки [ydl](https://github.com/ytdl-org/youtube-dl) для загрузки видео, а так же [rich](https://github.com/Textualize/rich) для оформления консольного и [pywebview](https://github.com/r0x0r/pywebview) для графического интерфейсов. Для работы с кодеками используется [FFMPEG](https://ffmpeg.org/), он уже скачан и размещен в папке программы.

### Актуальная версия с графическим интерфейсом: 
<img src="https://github.com/user-attachments/assets/1ed99021-0620-4772-a853-24ce66bb7ae8" width="600">


### --Classic, консольное приложение:
<img src="https://github.com/user-attachments/assets/9b14f2e2-299f-4740-bcfa-a9d411f701ed" width="600">

## Загрузка

**[Актуальная версия](https://github.com/Rayness/YouTube-Downloader/releases/tag/v3.2.0-beta)** - консольное приложение и графический интерфейс.

## Как запустить:
- Если использовался "установщик" (YT-Downloader.exe), то на рабочем столе появится ярлык запуска и можно использовать его;
- В папке с программой имеются три файла для запуска:
  - launch --Classic.bat - запускает классическое консольное приложение;
  - launch gui.bat - запускает графический интерфейс вместе с консолью;
  - run.vbs - запускает файл launch gui.bat, но без консоли ( этот файл и запускается с помощью ярлыка на рабочем столе ).


## Как пользоваться:
После запуска графического интерфейса необходимо:
 1. Вставить ссылку на видео ( скопировать из строки url в браузере );
 2. Выбрать необходимый формат и качество видео ( по умолчанию видео будет загружено в mp4 в FullHD );
 3. Нажать на кнопку "Добавить в очередь";
 4. Повторить первые три пункта столько раз, сколько необходимо, либо переходить к пятому;
 5. Нажать кнопку "Начать загрузку";
 6. Дождаться окончания загрузки всех видео, либо закрыть программу, если хочется, очередь сохранится;
    - Если закрыли программу, то запустити её и повторите действие из пятого пункта, но в этот раз не закрывая программу.
 7. После загрузки откроется папка с загруженными видео и можно закрывать программу.


## Известные баги:
- Видео, в названии которых присутствуют ковычки ("") не смогут добавиться в очередь загрузки;
- После скачивания видео, оно не удаляется из локальной очереди ( файл queue.json ).
  - Видео можно будет удалить из очереди через кнопку "Удалить" около видео при следующем запуске.


## Дальнейшие планы:
- [ ] Добавить автообновление;
- [ ] Перенести проект на Electron ( когда-нибудь );
- [ ] Сделать мобильное приложение ( очень не скоро )

## Лицензия

Проект YT-Downloader распространяется по лицензии MIT.
