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

## Дальнейшие планы:
- [ ] Добавить автообновление;
- [ ] Перенести проект на Electron ( когда-нибудь ).

## Известные баги:
- Видео, в названии которых присутствуют ковычки ("") не смогут добавиться в очередь загрузки;
- После скачивания видео, оно не удаляется из локальной очереди ( файл queue.json ).

## Лицензия

Проект YT-Downloader распространяется по лицензии MIT.
