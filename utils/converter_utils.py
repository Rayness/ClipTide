import os
import ffmpeg


def format_duration(seconds):
    # Конвертируем секунды в нормальный формат
    hours = int(seconds // 3600)
    minute = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minute:02d}:{seconds:02d}"

def print_video_info(file_path):
    print("Путь: ", file_path)
    if not os.path.exists(file_path):
        return f"Файл не найден: {file_path}"
    
    if not os.access(file_path, os.R_OK):
        return f"Нет прав на чтение файла: {file_path}"
    try:
        # Получает данные 
        probe = ffmpeg.probe(file_path)
        # 
        format_info = probe.get("format", {})
        duration = float(format_info.get("duration", 0))
        bitrate = int(format_info.get("bit_rate", 0)) / 1000 # кбит/с

        # Видеопоток
        video_stream = next(
            (s for s in probe.get("streams", []) if s.get("codec_type") == "video"),
            None
        )

        if not video_stream:
            print("Поток не найден")
            return

        width = video_stream.get("width", "?")
        height = video_stream.get("height", "?")
        codec = video_stream.get("codec_name", "?")
        fps = video_stream.get("r_frame_rate", "?")
        if "/" in fps:
            fps = eval(fps)

        # Аудиопоток
        audio_stream = next(
            (s for s in probe.get("streams", []) if s.get("codec_type") == "audio"),
            None
        )
        audio_codec = audio_stream.get("codec_name", "нет") if audio_stream else "нет"
        audio_bitrate = int(audio_stream.get("bit_rate", 0)) / 1000 if audio_stream else 0
        
        return round(duration), round(bitrate), width, height, codec, round(fps), audio_codec, round(audio_bitrate)
    except ffmpeg.Error as e:
        print(f"Ошибка FFmpeg: {e.stderr.decode()}")
        return f"Ошибка FFmpeg: {e.stderr.decode()}"
    except Exception as e:
        print(f"Ошибка: {e}")
        return f"Ошибка: {e}"

def get_thumbnail_base64(video_path, use_first_frame_if_no_thumbnail=True):
    import base64
    try:
        # Проверяем наличие встроенной обложки
        probe = ffmpeg.probe(video_path)
        has_thumbnail = any(
            stream.get('disposition', {}).get('attached_pic', 0) == 1
            for stream in probe.get('streams', [])
        )
        
        # Если есть встроенная обложка - извлекаем её
        if has_thumbnail:
            out, _ = (
                ffmpeg.input(video_path)
                .output('pipe:', format='image2', vcodec='mjpeg', vframes=1)
                .run(capture_stdout=True, capture_stderr=True)
            )
        # Иначе генерируем превью из первого кадра
        elif use_first_frame_if_no_thumbnail:
            out, _ = (
                ffmpeg.input(video_path, ss='00:00:05')  # Берём кадр в начале видео
                .output('pipe:', format='image2', vcodec='mjpeg', vframes=1)
                .run(capture_stdout=True, capture_stderr=True)
            )
        else:
            return None, "Встроенная обложка не найдена"
        
        # Конвертируем в base64
        img_base64 = base64.b64encode(out).decode('utf-8')
        return f"data:image/jpeg;base64,{img_base64}", None

    except ffmpeg.Error as e:
        return None, f"Ошибка FFmpeg: {e.stderr.decode()}"
    except Exception as e:
        return None, f"Ошибка: {str(e)}"