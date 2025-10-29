#!/usr/bin/env python3
"""
Тест индикатора офлайн (красный крест)
"""

import sys
from pathlib import Path
import time

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from display_manager import DisplayManager
from PIL import Image

# Конфигурация
DIVOOM_IP = "192.168.2.242"

# Конфигурация шрифтов (из config.yaml)
name_config = {
    'size': 10,
    'color': [255, 255, 255],
    'position': [2, 2],
    'stroke_width': 1,
    'stroke_color': [100, 100, 100],
    'font_path': './fonts/LanaPixel.ttf'
}

humidity_config = {
    'size': 18,
    'position': [2, 42],
    'stroke_width': 1,
    'stroke_color': [100, 100, 100],
    'font_path': './fonts/NorthrupExtended.ttf',
    'dynamic_color': True,
    'colors': {
        'low': [255, 50, 50],
        'normal': [50, 255, 100],
        'high': [100, 150, 255]
    }
}

datetime_config = {
    'enabled': True,
    'time': {
        'size': 10,
        'color': [200, 200, 200],
        'position': [2, 16],
        'stroke_width': 1,
        'stroke_color': [100, 100, 100],
        'font_path': './fonts/LanaPixel.ttf'
    },
    'date': {
        'size': 8,
        'color': [150, 150, 150],
        'position': [2, 28],
        'stroke_width': 1,
        'stroke_color': [100, 100, 100],
        'font_path': './fonts/LanaPixel.ttf'
    }
}


def test_offline_indicator():
    """Тестируем отображение офлайн индикатора"""

    print("=" * 50)
    print("Тест индикатора OFFLINE (красный крест)")
    print("=" * 50)

    # Инициализируем дисплей
    display = DisplayManager(DIVOOM_IP, images_dir="./images")

    # Тестовые данные
    test_cases = [
        {
            "name": "Алла",
            "humidity": 54,
            "threshold_min": 40,
            "threshold_max": 55,
            "is_online": True,
            "description": "Нормальный режим (ONLINE)"
        },
        {
            "name": "Гюзель",
            "humidity": 45,
            "threshold_min": 40,
            "threshold_max": 55,
            "is_online": False,
            "description": "Офлайн режим (красный крест)"
        }
    ]

    for idx, test in enumerate(test_cases, 1):
        print(f"\nТест {idx}/{len(test_cases)}: {test['description']}")
        print(f"  Растение: {test['name']}")
        print(f"  Влажность: {test['humidity']}%")
        print(f"  Статус: {'ONLINE' if test['is_online'] else 'OFFLINE'}")

        success = display.display_plant(
            plant_name=test['name'],
            humidity=test['humidity'],
            name_config=name_config,
            humidity_config=humidity_config,
            background_enabled=True,
            threshold_min=test['threshold_min'],
            threshold_max=test['threshold_max'],
            datetime_config=datetime_config,
            is_online=test['is_online']
        )

        if success:
            print("  ✓ Успешно отображено")
        else:
            print("  ✗ Ошибка при отображении")

        # Ждем 5 секунд перед следующим тестом
        if idx < len(test_cases):
            print("  Ожидание 5 сек...")
            time.sleep(5)

    print("\n" + "=" * 50)
    print("Тест завершен!")
    print("=" * 50)


if __name__ == "__main__":
    test_offline_indicator()
