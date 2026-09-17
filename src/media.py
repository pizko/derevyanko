#!/usr/bin/env python3
"""Фото для лендинга СК Деревянко: только реальные объекты с sk-derevyanko.ru.

Исходники лежат в orig/uploads (скачаны из wp-content/uploads, в git не попадают).
На выходе — AVIF и WebP в двух ширинах + meta.json с пропорциями.
Обработка сдержанная: чуть ниже насыщенность, немного плотнее тени — под тёмную вёрстку.

  python3 src/media.py
"""
import json, pathlib
from PIL import Image, ImageEnhance, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
U = ROOT / "orig/uploads/2025/09"
OUT = ROOT / "assets/img"

PHOTOS = {
    # ЖК Прайм парк
    "prime-spalnya": "photo_2025-09-03_14-50-56.jpg",
    "prime-vannaya": "photo_2025-09-03_14-50-52.jpg",
    "prime-zerkalo": "photo_2025-09-03_14-50-54-2.jpg",
    "prime-dush": "photo_2025-09-03_14-50-55-2.jpg",
    "prime-shkaf": "photo_2025-09-03_14-50-52-2.jpg",
    # ЖК Скай Хаус
    "sky-gostinaya": "photo_2025-09-03_14-43-57.jpg",
    "sky-kuhnya": "photo_2025-09-03_14-43-51-3.jpg",
    "sky-sanuzel": "photo_2025-09-03_14-43-54.jpg",
    "sky-kollektor": "photo_2025-09-03_14-43-55-2.jpg",
    # Шелепиха
    "shel-gostinaya": "photo_2025-05-22_13-6.jpg",
    "shel-stolovaya": "photo_2025-05-22_13-5.jpg",
    "shel-koridor": "photo_2025-05-22_13-7.jpg",
    "shel-spalnya": "photo_2025-05-22_13-2.jpg",
    "shel-spalnya-2": "photo_2025-05-22_13-3.jpg",
    # ЖК Энитео
    "eni-vannaya": "photo_2025-09-03_14-47-32.jpg",
    "eni-koridor": "pf3544356hoto_2025-09-03_14-.jpg",
    "eni-pol": "photo_2025-09-03_14-47-30-2.jpg",
    "eni-komnata": "photo_2025-09-03_14-47-33.jpg",
    # Большая Очаковская 2
    "ochak-tv": "photo_2025-07-30_21-1-1.jpg",
    "ochak-stolovaya": "666photo_2025-07-30_21-.jpg.webp",
    # Детский центр
    "detsky-karta": "852photo_2025-09-03_14-.jpg",
    "detsky-holl": "987photo_2025-09-03_14-.jpg",
    # Новокузнецкая
    "novok-komnata": "pidinahoito_2025-09-03_14-.jpg.webp",
    "novok-vannaya": "1.jpg-1.webp",
}


def grade(im):
    im = ImageOps.exif_transpose(im).convert("RGB")
    im = ImageEnhance.Color(im).enhance(0.86)
    im = ImageEnhance.Contrast(im).enhance(1.06)
    return ImageEnhance.Brightness(im).enhance(0.96)


def save(im, name, widths=(640, 1280)):
    for w in widths:
        k = im.copy()
        if k.width > w:
            k = k.resize((w, round(k.height * w / k.width)), Image.LANCZOS)
        k.save(OUT / f"{name}-{w}.webp", "WEBP", quality=78, method=6)
        k.save(OUT / f"{name}-{w}.avif", "AVIF", quality=58)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {}
    for name, src in PHOTOS.items():
        im = grade(Image.open(U / src))
        meta[name] = {"w": im.width, "h": im.height}
        save(im, name)
    # основатель: вырезка на прозрачном фоне с белым ореолом — кладём на светлую плашку
    f = Image.open(U / "photo_2.png.webp").convert("RGBA")
    bg = Image.new("RGBA", f.size, (237, 235, 230, 255))
    bg.alpha_composite(f)
    f = ImageEnhance.Color(bg.convert("RGB")).enhance(0.9)
    meta["osnovatel"] = {"w": f.width, "h": f.height}
    save(f, "osnovatel", (480,))
    # превью для соцсетей
    og = grade(Image.open(U / PHOTOS["prime-spalnya"]))
    og = ImageOps.fit(og, (1200, 630), Image.LANCZOS)
    og.save(OUT / "og.jpg", "JPEG", quality=82, optimize=True)
    (OUT / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print("фото:", len(meta))


if __name__ == "__main__":
    main()
