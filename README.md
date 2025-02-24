[![Supported Python Versions](https://img.shields.io/badge/python-3.12%20%7C%203.13-%234B8BBE)](https://www.python.org/downloads/) [![Downloads](https://img.shields.io/github/downloads/Rayness/YouTube-Downloader/total)](https://github.com/Rayness/YouTube-Downloader/releases) [![Release date](https://img.shields.io/github/release-date/Rayness/YouTube-Downloader)]() [![Version tag](https://img.shields.io/github/v/tag/Rayness/YouTube-Downloader)]()

![YT-downloader](https://github.com/user-attachments/assets/6c9eaace-f0aa-4924-8498-bed1be55ca97)

[English Readme](https://github.com/Rayness/YouTube-Downloader/blob/main/README.md)
• [Russian Readme](https://github.com/Rayness/YouTube-Downloader/blob/main/README.ru.md)

## General information
> [!NOTE]
> This small program is designed to download video content in audio and video formats from the YouTube video hosting, but other platforms are also supported, such as: Rutube, Vkvideo, ok and many others. Everything works in Python using the [ydl](https://github.com/ytdl-org/youtube-dl) library for loading videos, as well as [rich](https://github.com/Textualize/rich) for designing the console and [pywebview](https://github.com/r0x0r/pywebview) for the graphical interface. [FFMPEG](https://ffmpeg.org/) is used to work with codecs, it has already been downloaded and placed in the program folder.

### Current version with graphical interface:
<img src="https://github.com/user-attachments/assets/f232632a-2167-4aca-9d9d-903567110e1d" width="600">

### --Classic, console application:
<img src="https://github.com/user-attachments/assets/9b14f2e2-299f-4740-bcfa-a9d411f701ed" width="600">

## Download

**[Current version](https://github.com/Rayness/YouTube-Downloader/releases/tag/v3.2.0-beta)** - console application and graphical interface.

## How to run:
- If the "installer" (YT-Downloader.exe) was used, a launch shortcut will appear on the desktop and you can use it;
    - There are three files for launching in the program folder:
    - launch --Classic.bat - launches the classic console application;
    - launch gui.bat - launches the graphical interface together with the console;
    - run.vbs - launches the launch gui.bat file, but without the console (this file is launched using the shortcut on the desktop).

## How to use:
After launching the graphical interface, you need to:
1. Paste the link to the video (copy from the url line in the browser);
2. Select the desired video format and quality (by default, the video will be downloaded in mp4 in FullHD);
3. Click the "Add to queue" button;
4. Repeat the first three steps as many times as necessary, or go to the fifth;
5. Click the "Start download" button;
6. Wait until all videos are downloaded, or close the program if you want, the queue will be saved;
    - If you closed the program, then launch it and repeat the action from point 5, but this time without closing the program.
7. After downloading, the folder with the downloaded videos will open and you can close the program.

## Known bugs:
- Videos with quotes ("") in their names cannot be added to the download queue;
- After downloading a video, it is not removed from the local queue (file queue.json).
- The video can be removed from the queue using the "Delete" button next to the video the next time it is launched.

## Future plans:
- [ ] Add auto-update;
- [ ] Transfer the project to Electron (someday);
- [ ] Make a mobile application (very soon).

## License

The YT-Downloader project is distributed under the MIT license.
