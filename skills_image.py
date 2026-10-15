# -*- coding: utf-8 -*-
"""Навыки Ульвара: изображения."""
from skills import skill, _ok, _err, downloads_folder
import os
import time


def _out(path, suffix):
    base, ext = os.path.splitext(path)
    return f"{base}_{suffix}{ext or '.png'}"


@skill("Изображения", "Повернуть картинку на угол")
def rotate_image(path, degrees=90, out=None):
    try:
        from PIL import Image
        im = Image.open(path).rotate(-float(degrees), expand=True)
        out = out or _out(path, f"rot{degrees}")
        im.save(out); return _ok(out)
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Сделать чёрно-белой")
def grayscale_image(path, out=None):
    try:
        from PIL import Image
        out = out or _out(path, "bw")
        Image.open(path).convert("L").save(out); return _ok(out)
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Обрезать картинку (x, y, ширина, высота)")
def crop_image(path, x, y, w, h, out=None):
    try:
        from PIL import Image
        im = Image.open(path)
        im = im.crop((int(x), int(y), int(x)+int(w), int(y)+int(h)))
        out = out or _out(path, "crop"); im.save(out); return _ok(out)
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Сделать миниатюру (thumbnail)")
def thumbnail(path, size=256, out=None):
    try:
        from PIL import Image
        im = Image.open(path); im.thumbnail((int(size), int(size)))
        out = out or _out(path, "thumb"); im.save(out); return _ok(out)
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Зеркально отразить (horizontal/vertical)")
def flip_image(path, mode="horizontal", out=None):
    try:
        from PIL import Image, ImageOps
        im = Image.open(path)
        im = ImageOps.mirror(im) if mode == "horizontal" else ImageOps.flip(im)
        out = out or _out(path, "flip"); im.save(out); return _ok(out)
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Размыть картинку")
def blur_image(path, radius=4, out=None):
    try:
        from PIL import Image, ImageFilter
        im = Image.open(path).filter(ImageFilter.GaussianBlur(float(radius)))
        out = out or _out(path, "blur"); im.save(out); return _ok(out)
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Повысить резкость")
def sharpen_image(path, out=None):
    try:
        from PIL import Image, ImageFilter
        im = Image.open(path).filter(ImageFilter.SHARPEN)
        out = out or _out(path, "sharp"); im.save(out); return _ok(out)
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Изменить яркость (1.0 — без изменений)")
def image_brightness(path, factor=1.3, out=None):
    try:
        from PIL import Image, ImageEnhance
        im = ImageEnhance.Brightness(Image.open(path)).enhance(float(factor))
        out = out or _out(path, "bright"); im.save(out); return _ok(out)
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Изменить контраст")
def image_contrast(path, factor=1.3, out=None):
    try:
        from PIL import Image, ImageEnhance
        im = ImageEnhance.Contrast(Image.open(path)).enhance(float(factor))
        out = out or _out(path, "contrast"); im.save(out); return _ok(out)
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Добавить текстовый водяной знак")
def watermark(path, text="Ульвар", out=None):
    try:
        from PIL import Image, ImageDraw
        im = Image.open(path).convert("RGBA")
        d = ImageDraw.Draw(im)
        d.text((10, im.height-30), text, fill=(255, 255, 255, 180))
        out = out or _out(path, "wm"); im.convert("RGB").save(out); return _ok(out)
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Размер и формат картинки")
def image_info(path):
    try:
        from PIL import Image
        im = Image.open(path)
        return f"{im.width}x{im.height}, формат {im.format}, режим {im.mode}"
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "EXIF-данные фото (камера, дата)")
def image_exif(path):
    try:
        from PIL import Image
        exif = Image.open(path)._getexif() or {}
        from PIL.ExifTags import TAGS
        out = [f"{TAGS.get(k, k)}: {v}" for k, v in exif.items() if TAGS.get(k, k) in
               ("Make", "Model", "DateTime", "ExposureTime", "ISOSpeedRatings")]
        return "\n".join(out) or "(нет EXIF)"
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Собрать несколько картинок в коллаж (горизонтально)")
def collage(paths, out=None):
    try:
        from PIL import Image
        if isinstance(paths, str):
            paths = paths.split(";")
        ims = [Image.open(p.strip()) for p in paths]
        h = min(i.height for i in ims)
        ims = [i.resize((int(i.width*h/i.height), h)) for i in ims]
        total = sum(i.width for i in ims)
        canvas = Image.new("RGB", (total, h), "white")
        x = 0
        for i in ims:
            canvas.paste(i, (x, 0)); x += i.width
        out = out or os.path.join(downloads_folder(), f"collage_{int(time.time())}.png")
        canvas.save(out); return _ok(out)
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Создать QR-код с текстом/ссылкой")
def make_qr(text, out=None):
    try:
        import qrcode
        img = qrcode.make(text)
        out = out or os.path.join(downloads_folder(), f"qr_{int(time.time())}.png")
        img.save(out); return _ok(out)
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Прочитать QR-код с картинки")
def read_qr(path):
    try:
        import cv2
        img = cv2.imread(path)
        data, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
        return data or "(QR не распознан)"
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Найти лица на фото (сколько)")
def detect_faces(path):
    try:
        import cv2
        img = cv2.imread(path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = cc.detectMultiScale(gray, 1.1, 4)
        return f"Найдено лиц: {len(faces)}"
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Средний цвет картинки")
def average_color(path):
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB").resize((1, 1))
        return f"Средний цвет RGB: {im.getpixel((0,0))}"
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Добавить рамку вокруг картинки")
def add_border(path, size=20, color="black", out=None):
    try:
        from PIL import Image, ImageOps
        im = ImageOps.expand(Image.open(path), border=int(size), fill=color)
        out = out or _out(path, "border"); im.save(out); return _ok(out)
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Склеить картинки вертикально")
def stack_vertical(paths, out=None):
    try:
        from PIL import Image
        if isinstance(paths, str):
            paths = paths.split(";")
        ims = [Image.open(p.strip()) for p in paths]
        w = min(i.width for i in ims)
        ims = [i.resize((w, int(i.height*w/i.width))) for i in ims]
        total = sum(i.height for i in ims)
        canvas = Image.new("RGB", (w, total), "white")
        y = 0
        for i in ims:
            canvas.paste(i, (0, y)); y += i.height
        out = out or os.path.join(downloads_folder(), f"stack_{int(time.time())}.png")
        canvas.save(out); return _ok(out)
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Сжать JPG (уменьшить размер файла)")
def compress_image(path, quality=60, out=None):
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB")
        out = out or _out(path, "min")
        if not out.lower().endswith((".jpg", ".jpeg")):
            out = os.path.splitext(out)[0] + ".jpg"
        im.save(out, "JPEG", quality=int(quality), optimize=True)
        return _ok(f"{out} ({os.path.getsize(out)//1024} КБ)")
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Негатив (инвертировать цвета)")
def invert_image(path, out=None):
    try:
        from PIL import Image, ImageOps
        im = ImageOps.invert(Image.open(path).convert("RGB"))
        out = out or _out(path, "neg"); im.save(out); return _ok(out)
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Сепия (винтажный эффект)")
def sepia(path, out=None):
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB")
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b = px[x, y]
                px[x, y] = (min(255, int(0.393*r+0.769*g+0.189*b)),
                            min(255, int(0.349*r+0.686*g+0.168*b)),
                            min(255, int(0.272*r+0.534*g+0.131*b)))
        out = out or _out(path, "sepia"); im.save(out); return _ok(out)
    except Exception as e:
        return _err(str(e))


@skill("Изображения", "Создать картинку сплошного цвета")
def solid_color_image(width=400, height=400, color="#3366ff", out=None):
    try:
        from PIL import Image
        im = Image.new("RGB", (int(width), int(height)), color)
        out = out or os.path.join(downloads_folder(), f"color_{int(time.time())}.png")
        im.save(out); return _ok(out)
    except Exception as e:
        return _err(str(e))
