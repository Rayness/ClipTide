[![Supported Python Versions](https://img.shields.io/badge/python-3.12%20%7C%203.13-%234B8BBE)](https://www.python.org/downloads/) [![Downloads](https://img.shields.io/github/downloads/Rayness/YouTube-Downloader/total)](https://github.com/Rayness/YouTube-Downloader/releases) [![Release date](https://img.shields.io/github/release-date/Rayness/YouTube-Downloader)]() [![Version tag](https://img.shields.io/github/v/tag/Rayness/YouTube-Downloader)]()

![YT-downloader](https://github.com/user-attachments/assets/6c9eaace-f0aa-4924-8498-bed1be55ca97)

[English Readme](https://github.com/Rayness/YouTube-Downloader/blob/main/README.md)
• [Russian Readme](https://github.com/Rayness/YouTube-Downloader/blob/main/README.ru.md)

## General information
This small program is designed to download video content in audio and video formats from the YouTube video hosting, but other platforms are also supported, such as: Rutube, Vkvideo, ok and many others. The full list can be found [here](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md), most likely videos will be downloaded from all these sources if they (the sources) are not blocked in your country.

> [!NOTE]
> Downloading video content is implemented using [yt-dlp](https://github.com/yt-dlp/yt-dlp). The graphical interface runs on [pywebview](https://github.com/r0x0r/pywebview). The program also has [FFMPEG](https://ffmpeg.org/) embedded in it.

### Current version with graphical interface (Outdated):
<img src="https://github.com/user-attachments/assets/50653621-2a6c-44bd-b75e-0c81b438c9ce" width="600">

## Download

**[Current version](https://github.com/Rayness/YouTube-Downloader/releases/tag/v2.0.3)** - 2.0.3

## How to run:
- Like any other application;
- If you downloaded the installer, then run it and follow the installation instructions;
- If you downloaded the archive, then extract the contents to any folder and run "YT-Downloader"

## How to use:
After launching the graphical interface, you need to:
1. Paste the link to the video (copy from the url line in the browser);
2. Select the desired video format and quality (by default, the video will be downloaded in mp4 in FullHD);
3. Click the "Add to queue" button;
4. Repeat the first three steps as many times as necessary, or go to the fifth;
5. Click the "Start download" button;
6. Wait until all the videos are downloaded, or close the program if you want, the queue will be saved;
- If you closed the program, then launch it and repeat the action from the fifth step, but this time without closing the program.
7. After downloading, the folder with the downloaded videos will open and you can close the program.

## Known errors:
1. Problem: Incorrect display of playlist downloads, how to determine: the indicator spins for a very long time and nothing happens for a long time. If you wait, the playlist name will appear in the queue without a preview. The entire playlist will be downloaded.
- Solution: Do not add playlists to the queue, or wait;

2. Some videos with certain symbols may not be added to the download queue.
- Solution: Send the error to issue and wait for the problematic Unicode character to be added to the program exceptions, or enable a special setting in the system.

3. After clicking the "delete" button, the video may not be deleted from the interface, although it is no longer in the queue itself.
- Solution: Restarting the program.

## Future plans:
- [x] Add auto-update ( Updater added );
- [ ] Transfer the project to Electron ( someday );
- [ ] Make a mobile application ( not very soon )

## License

The YT-Downloader project is distributed under the MIT license.
