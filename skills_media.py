# -*- coding: utf-8 -*-
"""Навыки Ульвара: видео и аудио (ffmpeg)."""
from skills import skill, _ok, _err
import os
import subprocess
import shutil

FFMPEG = r"C:\Ulvar\bin\ffmpeg.exe"
FFPROBE = r"C:\Ulvar\bin\ffprobe.exe"


def _ff():
    if os.path.exists(FFMPEG):
        return FFMPEG
    return shutil.which("ffmpeg") or FFMPEG


def _probe():
    if os.path.exists(FFPROBE):
        return FFPROBE
    return shutil.which("ffprobe") or FFPROBE


def _run(args, timeout=600):
    try:
        r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout)
        return (r.stdout + r.stderr)
    except Exception as e:
        return f"ERR {e}"


def _out(path, suffix, ext=None):
    base, e = os.path.splitext(path)
    return f"{base}_{suffix}{ext or e}"


@skill("Медиа", "Инфо о медиафайле (длительность, кодеки)")
def media_info(path):
    out = _run([_probe(), "-hide_banner", path])
    keep = [l.strip() for l in out.splitlines() if "Duration" in l or "Stream" in l]
    return "\n".join(keep) or out[-1500:]


@skill("Медиа", "Конвертировать видео в другой формат (напр. mp4)")
def convert_video(path, to="mp4", out=None):
    out = out or os.path.splitext(path)[0] + "." + to
    r = _run([_ff(), "-y", "-i", path, out])
    return _ok(out) if os.path.exists(out) else _err(r[-800:])


@skill("Медиа", "Извлечь звук из видео (в mp3)")
def extract_audio(path, out=None):
    out = out or os.path.splitext(path)[0] + ".mp3"
    r = _run([_ff(), "-y", "-i", path, "-q:a", "0", "-map", "a", out])
    return _ok(out) if os.path.exists(out) else _err(r[-800:])


@skill("Медиа", "Вырезать фрагмент видео (с HH:MM:SS, длительность сек)")
def trim_video(path, start="00:00:00", duration=10, out=None):
    out = out or _out(path, "trim")
    r = _run([_ff(), "-y", "-ss", str(start), "-i", path, "-t", str(duration), "-c", "copy", out])
    return _ok(out) if os.path.exists(out) else _err(r[-800:])


@skill("Медиа", "Сжать видео (уменьшить размер)")
def compress_video(path, crf=28, out=None):
    out = out or _out(path, "small")
    r = _run([_ff(), "-y", "-i", path, "-vcodec", "libx264", "-crf", str(crf), out])
    return _ok(out) if os.path.exists(out) else _err(r[-800:])


@skill("Медиа", "Видео → GIF")
def video_to_gif(path, fps=10, width=480, out=None):
    out = out or os.path.splitext(path)[0] + ".gif"
    r = _run([_ff(), "-y", "-i", path, "-vf", f"fps={fps},scale={width}:-1", out])
    return _ok(out) if os.path.exists(out) else _err(r[-800:])


@skill("Медиа", "Кадр из видео в указанную секунду")
def video_frame(path, seconds=1, out=None):
    out = out or _out(path, f"frame{seconds}", ".png")
    r = _run([_ff(), "-y", "-ss", str(seconds), "-i", path, "-frames:v", "1", out])
    return _ok(out) if os.path.exists(out) else _err(r[-800:])


@skill("Медиа", "Изменить разрешение видео (ширина)")
def resize_video(path, width=1280, out=None):
    out = out or _out(path, f"w{width}")
    r = _run([_ff(), "-y", "-i", path, "-vf", f"scale={width}:-2", out])
    return _ok(out) if os.path.exists(out) else _err(r[-800:])


@skill("Медиа", "Убрать звук из видео")
def mute_video(path, out=None):
    out = out or _out(path, "mute")
    r = _run([_ff(), "-y", "-i", path, "-an", "-c:v", "copy", out])
    return _ok(out) if os.path.exists(out) else _err(r[-800:])


@skill("Медиа", "Изменить скорость видео (2.0 = в 2 раза быстрее)")
def speed_video(path, factor=2.0, out=None):
    out = out or _out(path, f"x{factor}")
    pts = 1.0 / float(factor)
    r = _run([_ff(), "-y", "-i", path, "-filter:v", f"setpts={pts}*PTS",
              "-filter:a", f"atempo={factor}", out])
    return _ok(out) if os.path.exists(out) else _err(r[-800:])


@skill("Медиа", "Повернуть видео на 90°")
def rotate_video(path, out=None):
    out = out or _out(path, "rot")
    r = _run([_ff(), "-y", "-i", path, "-vf", "transpose=1", out])
    return _ok(out) if os.path.exists(out) else _err(r[-800:])


@skill("Медиа", "Конвертировать аудио (напр. в mp3/wav)")
def convert_audio(path, to="mp3", out=None):
    out = out or os.path.splitext(path)[0] + "." + to
    r = _run([_ff(), "-y", "-i", path, out])
    return _ok(out) if os.path.exists(out) else _err(r[-800:])


@skill("Медиа", "Обрезать аудио (с секунды, длительность)")
def trim_audio(path, start=0, duration=30, out=None):
    out = out or _out(path, "trim")
    r = _run([_ff(), "-y", "-ss", str(start), "-i", path, "-t", str(duration), "-c", "copy", out])
    return _ok(out) if os.path.exists(out) else _err(r[-800:])


@skill("Медиа", "Громкость аудио (1.5 = +50%)")
def change_volume(path, factor=1.5, out=None):
    out = out or _out(path, "vol")
    r = _run([_ff(), "-y", "-i", path, "-filter:a", f"volume={factor}", out])
    return _ok(out) if os.path.exists(out) else _err(r[-800:])


@skill("Медиа", "Нормализовать громкость аудио")
def normalize_audio(path, out=None):
    out = out or _out(path, "norm")
    r = _run([_ff(), "-y", "-i", path, "-filter:a", "loudnorm", out])
    return _ok(out) if os.path.exists(out) else _err(r[-800:])


@skill("Медиа", "Склеить два видео подряд")
def concat_videos(path1, path2, out="concat.mp4"):
    try:
        lst = os.path.join(os.path.dirname(os.path.abspath(path1)), "_concat.txt")
        with open(lst, "w", encoding="utf-8") as f:
            f.write(f"file '{os.path.abspath(path1)}'\nfile '{os.path.abspath(path2)}'\n")
        r = _run([_ff(), "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out])
        os.remove(lst)
        return _ok(out) if os.path.exists(out) else _err(r[-800:])
    except Exception as e:
        return _err(str(e))


@skill("Медиа", "Наложить звук на видео")
def add_audio_to_video(video, audio, out="withaudio.mp4"):
    r = _run([_ff(), "-y", "-i", video, "-i", audio, "-c:v", "copy", "-map", "0:v:0",
              "-map", "1:a:0", "-shortest", out])
    return _ok(out) if os.path.exists(out) else _err(r[-800:])


@skill("Медиа", "Видео → серия кадров (картинок)")
def video_to_frames(path, fps=1, out_dir=None):
    out_dir = out_dir or os.path.splitext(path)[0] + "_frames"
    os.makedirs(out_dir, exist_ok=True)
    r = _run([_ff(), "-y", "-i", path, "-vf", f"fps={fps}", os.path.join(out_dir, "frame_%04d.png")])
    n = len([f for f in os.listdir(out_dir) if f.endswith(".png")])
    return _ok(f"{n} кадров → {out_dir}") if n else _err(r[-800:])


@skill("Медиа", "Длительность медиафайла в секундах")
def media_duration(path):
    out = _run([_probe(), "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", path])
    return out.strip()[:40] or "(не определить)"


@skill("Медиа", "Проверить, установлен ли ffmpeg")
def ffmpeg_check():
    f = _ff()
    return _ok(f"ffmpeg: {f}") if os.path.exists(f) or shutil.which("ffmpeg") else _err("ffmpeg не найден")
