# -*- coding: utf-8 -*-
"""Навыки Ульвара: автоматизация и пакетные операции."""
from skills import skill, _ok, _err
import os
import glob
import shutil
import time
import threading


@skill("Автоматизация", "Пакетно переименовать файлы (добавить префикс)")
def batch_rename_prefix(folder, prefix, ext="*"):
    try:
        cnt = 0
        for p in glob.glob(os.path.join(folder, ext if ext.startswith("*") else f"*.{ext}")):
            d, name = os.path.split(p)
            os.rename(p, os.path.join(d, prefix + name)); cnt += 1
        return _ok(f"переименовано: {cnt}")
    except Exception as e:
        return _err(str(e))


@skill("Автоматизация", "Пакетно переименовать по шаблону (имя_1, имя_2, …)")
def batch_rename_sequence(folder, base_name, ext="jpg"):
    try:
        files = sorted(glob.glob(os.path.join(folder, f"*.{ext}")))
        for i, p in enumerate(files, 1):
            os.rename(p, os.path.join(folder, f"{base_name}_{i}.{ext}"))
        return _ok(f"переименовано: {len(files)}")
    except Exception as e:
        return _err(str(e))


@skill("Автоматизация", "Разложить файлы по папкам по расширению")
def organize_by_extension(folder):
    try:
        moved = 0
        for p in glob.glob(os.path.join(folder, "*")):
            if os.path.isfile(p):
                ext = os.path.splitext(p)[1][1:].lower() or "без_расширения"
                dst = os.path.join(folder, ext)
                os.makedirs(dst, exist_ok=True)
                shutil.move(p, os.path.join(dst, os.path.basename(p))); moved += 1
        return _ok(f"разложено файлов: {moved}")
    except Exception as e:
        return _err(str(e))


@skill("Автоматизация", "Удалить пустые папки внутри директории")
def remove_empty_folders(folder):
    try:
        cnt = 0
        for root, dirs, files in os.walk(folder, topdown=False):
            for d in dirs:
                p = os.path.join(root, d)
                if not os.listdir(p):
                    os.rmdir(p); cnt += 1
        return _ok(f"удалено пустых папок: {cnt}")
    except Exception as e:
        return _err(str(e))


@skill("Автоматизация", "Найти дубликаты файлов (по содержимому)")
def find_duplicates(folder):
    import hashlib
    seen, dups = {}, []
    for root, _, files in os.walk(folder):
        for fn in files:
            p = os.path.join(root, fn)
            try:
                h = hashlib.md5(open(p, "rb").read()).hexdigest()
                if h in seen:
                    dups.append(f"{p}  =  {seen[h]}")
                else:
                    seen[h] = p
            except Exception:
                pass
    return "\n".join(dups[:50]) or "(дубликатов нет)"


@skill("Автоматизация", "Самые большие файлы в папке")
def largest_files(folder, top=10):
    files = []
    for root, _, fs in os.walk(folder):
        for fn in fs:
            p = os.path.join(root, fn)
            try:
                files.append((os.path.getsize(p), p))
            except Exception:
                pass
    files.sort(reverse=True)
    return "\n".join(f"{s/1e6:.1f} МБ  {p}" for s, p in files[:int(top)])


@skill("Автоматизация", "Файлы старше N дней")
def old_files(folder, days=30):
    cutoff = time.time() - int(days)*86400
    out = []
    for root, _, fs in os.walk(folder):
        for fn in fs:
            p = os.path.join(root, fn)
            try:
                if os.path.getmtime(p) < cutoff:
                    out.append(p)
            except Exception:
                pass
    return "\n".join(out[:50]) or "(нет старых файлов)"


@skill("Автоматизация", "Скопировать все файлы одного типа в папку")
def collect_files_by_type(folder, ext, dest):
    try:
        os.makedirs(dest, exist_ok=True)
        cnt = 0
        for p in glob.glob(os.path.join(folder, "**", f"*.{ext}"), recursive=True):
            shutil.copy2(p, dest); cnt += 1
        return _ok(f"скопировано {cnt} файлов .{ext} → {dest}")
    except Exception as e:
        return _err(str(e))


@skill("Автоматизация", "Резервная копия папки (zip с датой)")
def backup_folder(folder, dest_dir=None):
    try:
        dest_dir = dest_dir or os.path.dirname(os.path.abspath(folder))
        name = os.path.basename(os.path.abspath(folder)) + "_backup_" + time.strftime("%Y%m%d_%H%M")
        out = os.path.join(dest_dir, name)
        shutil.make_archive(out, "zip", folder)
        return _ok(f"бэкап: {out}.zip")
    except Exception as e:
        return _err(str(e))


@skill("Автоматизация", "Синхронизировать папку (скопировать новые/изменённые файлы)")
def sync_folders(src, dst):
    try:
        copied = 0
        for root, _, files in os.walk(src):
            rel = os.path.relpath(root, src)
            tgt = os.path.join(dst, rel)
            os.makedirs(tgt, exist_ok=True)
            for fn in files:
                s = os.path.join(root, fn); d = os.path.join(tgt, fn)
                if not os.path.exists(d) or os.path.getmtime(s) > os.path.getmtime(d):
                    shutil.copy2(s, d); copied += 1
        return _ok(f"синхронизировано файлов: {copied}")
    except Exception as e:
        return _err(str(e))


@skill("Автоматизация", "Пакетно конвертировать картинки в формат")
def batch_convert_images(folder, to="png"):
    try:
        from PIL import Image
        cnt = 0
        for p in glob.glob(os.path.join(folder, "*")):
            if p.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif")):
                try:
                    Image.open(p).convert("RGB").save(os.path.splitext(p)[0] + "." + to)
                    cnt += 1
                except Exception:
                    pass
        return _ok(f"сконвертировано: {cnt}")
    except Exception as e:
        return _err(str(e))


@skill("Автоматизация", "Пакетно изменить размер картинок")
def batch_resize_images(folder, width=1280):
    try:
        from PIL import Image
        cnt = 0
        for p in glob.glob(os.path.join(folder, "*")):
            if p.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                try:
                    im = Image.open(p)
                    h = int(im.height * int(width) / im.width)
                    im.resize((int(width), h)).save(p); cnt += 1
                except Exception:
                    pass
        return _ok(f"изменено: {cnt}")
    except Exception as e:
        return _err(str(e))


@skill("Автоматизация", "Объединить все txt-файлы папки в один")
def merge_text_files(folder, out="merged.txt"):
    try:
        with open(out, "w", encoding="utf-8") as o:
            for p in sorted(glob.glob(os.path.join(folder, "*.txt"))):
                o.write(f"\n===== {os.path.basename(p)} =====\n")
                o.write(open(p, encoding="utf-8", errors="replace").read())
        return _ok(f"объединено → {out}")
    except Exception as e:
        return _err(str(e))


@skill("Автоматизация", "Подсчитать все файлы по типам в папке")
def count_by_type(folder):
    import collections
    c = collections.Counter()
    for root, _, files in os.walk(folder):
        for fn in files:
            c[os.path.splitext(fn)[1].lower() or "без"] += 1
    return "\n".join(f"{ext}: {n}" for ext, n in c.most_common())


@skill("Автоматизация", "Следить за папкой N секунд и сообщить о новых файлах")
def watch_folder(folder, seconds=30):
    try:
        before = set(os.listdir(folder))
        time.sleep(float(seconds))
        after = set(os.listdir(folder))
        new = after - before
        return "Новые файлы:\n" + "\n".join(new) if new else "(новых файлов нет)"
    except Exception as e:
        return _err(str(e))


@skill("Автоматизация", "Создать несколько папок из списка (через запятую)")
def make_folders(parent, names):
    try:
        cnt = 0
        for n in names.split(","):
            os.makedirs(os.path.join(parent, n.strip()), exist_ok=True); cnt += 1
        return _ok(f"создано папок: {cnt}")
    except Exception as e:
        return _err(str(e))


@skill("Автоматизация", "Таймер обратного отсчёта (сигнал в конце)")
def countdown(seconds=60, message="Время вышло!"):
    def _t():
        time.sleep(float(seconds))
        try:
            import winsound
            winsound.Beep(1000, 500)
        except Exception:
            pass
        try:
            from skills import run_skill
            run_skill("notify", "Таймер Ульвара", message)
        except Exception:
            pass
    threading.Thread(target=_t, daemon=True).start()
    return _ok(f"таймер на {seconds}с запущен")


@skill("Автоматизация", "Очистить папку Загрузки от старых файлов (старше N дней)")
def clean_downloads(days=60):
    from skills import downloads_folder
    cutoff = time.time() - int(days)*86400
    cnt = 0
    for p in glob.glob(os.path.join(downloads_folder(), "*")):
        try:
            if os.path.isfile(p) and os.path.getmtime(p) < cutoff:
                os.remove(p); cnt += 1
        except Exception:
            pass
    return _ok(f"удалено старых файлов: {cnt}")


@skill("Автоматизация", "Общий размер папки")
def folder_size(folder):
    total = 0
    for root, _, files in os.walk(folder):
        for fn in files:
            try:
                total += os.path.getsize(os.path.join(root, fn))
            except Exception:
                pass
    return f"Размер {folder}: {total/1e9:.2f} ГБ ({total/1e6:.0f} МБ)"
