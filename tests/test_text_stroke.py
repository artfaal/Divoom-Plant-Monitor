#!/usr/bin/env python3
"""
Тест обводки текста на Divoom
"""

import sys
import time
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pixoo import Pixoo
from PIL import Image, ImageDraw, ImageFont
import os

PIXOO_ADDRESS = "192.168.2.242"

def get_font(size):
    """Получить шрифт"""
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except:
                pass

    return ImageFont.load_default()

def create_test_image(test_name, configs):
    """
    Создать тестовое изображение

    Args:
        test_name: Название теста
        configs: Список конфигов для тестирования
    """
    img = Image.new('RGB', (64, 64), color=(50, 50, 50))  # Серый фон
    draw = ImageDraw.Draw(img)

    y_offset = 5
    for config in configs:
        font = get_font(config['size'])
        draw.text(
            (config['x'], y_offset),
            config['text'],
            fill=tuple(config['color']),
            font=font,
            stroke_width=config.get('stroke_width', 0),
            stroke_fill=tuple(config.get('stroke_color', [0, 0, 0]))
        )
        y_offset += config['size'] + 5

    return img

def main():
    print(f"Подключение к {PIXOO_ADDRESS}...")
    pixoo = Pixoo(PIXOO_ADDRESS)
    print("✓ Подключено\n")

    tests = [
        {
            'name': 'Тест 1: Без обводки',
            'configs': [
                {'text': 'NO', 'size': 10, 'x': 2, 'color': [255, 255, 255], 'stroke_width': 0},
                {'text': 'STROKE', 'size': 10, 'x': 2, 'color': [100, 200, 255], 'stroke_width': 0},
            ]
        },
        {
            'name': 'Тест 2: Обводка 1px',
            'configs': [
                {'text': 'Алла', 'size': 12, 'x': 2, 'color': [255, 255, 255], 'stroke_width': 1, 'stroke_color': [0, 0, 0]},
                {'text': '54%', 'size': 16, 'x': 2, 'color': [100, 200, 255], 'stroke_width': 1, 'stroke_color': [0, 0, 0]},
            ]
        },
        {
            'name': 'Тест 3: Обводка 2px (текущая)',
            'configs': [
                {'text': 'Алла', 'size': 12, 'x': 2, 'color': [255, 255, 255], 'stroke_width': 2, 'stroke_color': [0, 0, 0]},
                {'text': '54%', 'size': 16, 'x': 2, 'color': [100, 200, 255], 'stroke_width': 2, 'stroke_color': [0, 0, 0]},
            ]
        },
        {
            'name': 'Тест 4: Обводка 3px',
            'configs': [
                {'text': 'Алла', 'size': 12, 'x': 2, 'color': [255, 255, 255], 'stroke_width': 3, 'stroke_color': [0, 0, 0]},
                {'text': '54%', 'size': 16, 'x': 2, 'color': [100, 200, 255], 'stroke_width': 3, 'stroke_color': [0, 0, 0]},
            ]
        },
        {
            'name': 'Тест 5: Цветная обводка',
            'configs': [
                {'text': 'Алла', 'size': 12, 'x': 2, 'color': [255, 255, 255], 'stroke_width': 2, 'stroke_color': [255, 0, 0]},
                {'text': '54%', 'size': 16, 'x': 2, 'color': [100, 200, 255], 'stroke_width': 2, 'stroke_color': [0, 255, 0]},
            ]
        },
        {
            'name': 'Тест 6: Белая обводка на темном фоне',
            'configs': [
                {'text': 'Алла', 'size': 12, 'x': 2, 'color': [0, 0, 0], 'stroke_width': 2, 'stroke_color': [255, 255, 255]},
                {'text': '54%', 'size': 16, 'x': 2, 'color': [50, 50, 50], 'stroke_width': 2, 'stroke_color': [255, 255, 255]},
            ]
        },
    ]

    try:
        for i, test in enumerate(tests):
            print(f"[{i+1}/{len(tests)}] {test['name']}")

            img = create_test_image(test['name'], test['configs'])

            pixoo.draw_image(img)
            pixoo.push()

            print(f"  ✓ Отображено на мониторе")

            # Ждем 3 секунды перед следующим тестом
            if i < len(tests) - 1:
                time.sleep(3)

        print("\n✓ Все тесты завершены!")
        print("  Последнее изображение останется на экране.")

    except KeyboardInterrupt:
        print("\n\nТест прерван пользователем")
        pixoo.clear()
        pixoo.push()

    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
