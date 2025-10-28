#!/usr/bin/env python3
"""
Тестовый скрипт для ротации сообщений на Divoom Pixoo 64
"""

import time
from pixoo import Pixoo
from PIL import Image, ImageDraw, ImageFont

def test_message_rotation():
    """Тест ротации двух сообщений каждые 2 секунды"""

    # IP адрес рамки
    PIXOO_ADDRESS = "192.168.2.242"

    # Сообщения для ротации
    messages = ["hello", "BB"]

    print(f"Подключение к Divoom Pixoo 64 по адресу: {PIXOO_ADDRESS}")

    try:
        # Создаем объект Pixoo
        pixoo = Pixoo(PIXOO_ADDRESS)
        print("✓ Подключение успешно!")
        print("\nНачинаю ротацию сообщений (Ctrl+C для остановки):")
        print("  Сообщение 1: 'hello'")
        print("  Сообщение 2: 'BB'")
        print("  Интервал: 2 секунды\n")

        # Бесконечный цикл ротации
        index = 0
        while True:
            message = messages[index]
            print(f"[{time.strftime('%H:%M:%S')}] Показываю: '{message}'")

            # Очищаем экран
            pixoo.clear()

            # Отправляем текст (центрируем по X и Y)
            x = 10
            y = 24
            r, g, b = 255, 255, 255
            pixoo.send_text_at_location_rgb(message, x, y, r, g, b)

            # Применяем изменения
            pixoo.push()

            # Ждем 2 секунды
            time.sleep(2)

            # Переключаем на следующее сообщение
            index = (index + 1) % len(messages)

    except KeyboardInterrupt:
        print("\n\n✓ Тест остановлен пользователем")
        # Очищаем экран
        pixoo.clear()
        pixoo.push()

    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False

    return True

if __name__ == "__main__":
    test_message_rotation()
