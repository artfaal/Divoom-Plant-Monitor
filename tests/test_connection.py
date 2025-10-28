#!/usr/bin/env python3
"""
Тестовый скрипт для проверки подключения к Divoom Pixoo 64
"""

from pixoo import Pixoo

def test_connection():
    """Проверка подключения к Divoom рамке"""

    # IP адрес рамки
    PIXOO_ADDRESS = "192.168.2.242"

    print(f"Попытка подключения к Divoom Pixoo 64 по адресу: {PIXOO_ADDRESS}")

    try:
        # Создаем объект Pixoo
        pixoo = Pixoo(PIXOO_ADDRESS)

        print("✓ Подключение успешно!")

        # Получаем информацию о устройстве
        print("\nИнформация о устройстве:")
        print(f"  IP: {PIXOO_ADDRESS}")
        print(f"  Размер: 64x64")

        # Пробуем получить яркость
        try:
            brightness = pixoo.get_brightness()
            print(f"  Текущая яркость: {brightness}%")
        except Exception as e:
            print(f"  Не удалось получить яркость: {e}")

        print("\n✓ Тест подключения пройден успешно!")
        return True

    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        print("\nПроверьте:")
        print("  1. Включена ли рамка")
        print("  2. Подключена ли рамка к той же сети")
        print("  3. Правильность IP адреса")
        return False

if __name__ == "__main__":
    test_connection()
