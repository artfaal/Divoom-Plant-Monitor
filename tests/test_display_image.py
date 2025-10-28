#!/usr/bin/env python3
"""
Тест отправки изображения на Divoom
"""

from pixoo import Pixoo
from PIL import Image, ImageDraw, ImageFont
import time

PIXOO_ADDRESS = "192.168.2.242"

print(f"Подключение к {PIXOO_ADDRESS}...")
pixoo = Pixoo(PIXOO_ADDRESS)
print("✓ Подключено")

# Создаем простое изображение
print("\nСоздание тестового изображения...")
img = Image.new('RGB', (64, 64), color=(0, 0, 0))
draw = ImageDraw.Draw(img)

# Рисуем белый текст
draw.text((10, 10), "TEST", fill=(255, 255, 255))
draw.text((10, 40), "123", fill=(100, 200, 255))

print("✓ Изображение создано")

# Пробуем разные методы
print("\n=== Тест 1: draw_image ===")
try:
    pixoo.draw_image(img)
    print("✓ draw_image выполнен успешно")
except Exception as e:
    print(f"✗ draw_image ошибка: {e}")

print("\n=== Тест 2: draw_image_at_location ===")
try:
    pixoo.draw_image_at_location(img, 0, 0)
    print("✓ draw_image_at_location выполнен успешно")
except Exception as e:
    print(f"✗ draw_image_at_location ошибка: {e}")

print("\n=== Тест 3: Проверяем, нужен ли push() ===")
try:
    pixoo.clear()
    time.sleep(0.5)

    # Рисуем пиксели напрямую
    for x in range(10, 30):
        for y in range(10, 30):
            pixoo.draw_pixel_at_location_rgb(x, y, 255, 0, 0)

    pixoo.push()
    print("✓ Пиксели + push() выполнены")
    time.sleep(2)

except Exception as e:
    print(f"✗ Ошибка с пикселями: {e}")

print("\n=== Тест 4: Конвертация изображения в массив ===")
try:
    pixoo.clear()
    time.sleep(0.5)

    # Попробуем конвертировать изображение в пиксели
    pixels = img.load()
    for y in range(64):
        for x in range(64):
            r, g, b = pixels[x, y]
            if r != 0 or g != 0 or b != 0:  # Рисуем только не-черные пиксели
                pixoo.draw_pixel_at_location_rgb(x, y, r, g, b)

    pixoo.push()
    print("✓ Изображение отправлено по пикселям + push()")

except Exception as e:
    print(f"✗ Ошибка: {e}")

print("\nТест завершен!")
