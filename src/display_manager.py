"""
Модуль для работы с Divoom дисплеем
"""

import os
import logging
from typing import Optional, Tuple
from pathlib import Path
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
from pixoo import Pixoo

logger = logging.getLogger(__name__)

# Словарь русских названий месяцев (сокращенные)
MONTH_NAMES_RU = {
    1: "янв", 2: "фев", 3: "мар", 4: "апр", 5: "май", 6: "июн",
    7: "июл", 8: "авг", 9: "сен", 10: "окт", 11: "ноя", 12: "дек"
}


class DisplayManager:
    """Менеджер для отображения информации на Divoom"""

    def __init__(self, ip_address: str, display_size: int = 64, images_dir: str = "./images"):
        """
        Инициализация менеджера

        Args:
            ip_address: IP адрес Divoom устройства
            display_size: Размер дисплея (по умолчанию 64x64)
            images_dir: Путь к папке с изображениями растений
        """
        self.ip_address = ip_address
        self.display_size = display_size
        self.images_dir = Path(images_dir)
        self.pixoo = Pixoo(ip_address)

        logger.info(f"DisplayManager инициализирован для {ip_address}")

    def _load_background(self, plant_name: str) -> Optional[Image.Image]:
        """
        Загрузить фоновое изображение для растения

        Args:
            plant_name: Имя растения (например: Алла)

        Returns:
            PIL Image или None, если изображение не найдено
        """
        # Пробуем разные расширения
        for ext in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']:
            image_path = self.images_dir / f"{plant_name}{ext}"
            if image_path.exists():
                try:
                    img = Image.open(image_path)
                    # Убедимся, что изображение нужного размера
                    if img.size != (self.display_size, self.display_size):
                        logger.warning(
                            f"Изображение {image_path} имеет размер {img.size}, "
                            f"изменяю на {self.display_size}x{self.display_size}"
                        )
                        img = img.resize((self.display_size, self.display_size), Image.Resampling.LANCZOS)
                    # Конвертируем в RGB если нужно
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    logger.debug(f"Загружено изображение: {image_path}")
                    return img
                except Exception as e:
                    logger.error(f"Ошибка при загрузке изображения {image_path}: {e}")

        logger.warning(f"Изображение для растения '{plant_name}' не найдено в {self.images_dir}")
        return None

    def _get_font(self, size: int, custom_font_path: Optional[str] = None) -> ImageFont.FreeTypeFont:
        """
        Получить шрифт нужного размера

        Args:
            size: Размер шрифта
            custom_font_path: Путь к пользовательскому TTF шрифту (опционально)

        Returns:
            PIL Font объект
        """
        # Если указан пользовательский шрифт - пробуем его первым
        if custom_font_path and os.path.exists(custom_font_path):
            try:
                logger.debug(f"Загружаю пользовательский шрифт: {custom_font_path}")
                return ImageFont.truetype(custom_font_path, size)
            except Exception as e:
                logger.warning(f"Не удалось загрузить пользовательский шрифт {custom_font_path}: {e}")

        # Пробуем разные системные шрифты
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except Exception as e:
                    logger.debug(f"Не удалось загрузить шрифт {font_path}: {e}")

        # Если не удалось загрузить TrueType шрифт, используем дефолтный
        logger.warning("Используется дефолтный шрифт")
        return ImageFont.load_default()

    def _get_humidity_color(
        self,
        humidity: int,
        threshold_min: int,
        threshold_max: int,
        humidity_config: dict
    ) -> Tuple[int, int, int]:
        """
        Определить цвет для отображения влажности на основе порогов

        Args:
            humidity: Текущая влажность
            threshold_min: Минимальный порог
            threshold_max: Максимальный порог
            humidity_config: Конфигурация шрифта влажности

        Returns:
            Кортеж RGB цвета
        """
        # Проверяем, включен ли динамический выбор цвета
        if not humidity_config.get('dynamic_color', False):
            return tuple(humidity_config.get('color', [100, 200, 255]))

        colors = humidity_config.get('colors', {})

        # Определяем уровень влажности
        if humidity < threshold_min:
            # Низкая влажность - красный
            color = colors.get('low', [255, 50, 50])
            level = "LOW"
        elif humidity > threshold_max:
            # Высокая влажность - синий
            color = colors.get('high', [100, 150, 255])
            level = "HIGH"
        else:
            # Нормальная влажность - зеленый
            color = colors.get('normal', [50, 255, 100])
            level = "NORMAL"

        logger.debug(
            f"Выбран цвет для влажности {humidity}% "
            f"(min: {threshold_min}, max: {threshold_max}): {level} {color}"
        )

        return tuple(color)

    def _format_time(self) -> str:
        """
        Форматировать текущее время в формате ЧЧ:ММ

        Returns:
            Строка времени (например: "23:00")
        """
        now = datetime.now()
        return now.strftime("%H:%M")

    def _format_date(self) -> str:
        """
        Форматировать текущую дату в формате "ДД месяц"

        Returns:
            Строка даты (например: "24 апр")
        """
        now = datetime.now()
        day = now.day
        month = MONTH_NAMES_RU[now.month]
        return f"{day} {month}"

    def create_plant_image(
        self,
        plant_name: str,
        humidity: int,
        name_config: dict,
        humidity_config: dict,
        background_enabled: bool = True,
        threshold_min: Optional[int] = None,
        threshold_max: Optional[int] = None,
        datetime_config: Optional[dict] = None,
        is_online: bool = True
    ) -> Image.Image:
        """
        Создать изображение с информацией о растении

        Args:
            plant_name: Имя растения
            humidity: Влажность (0-100)
            name_config: Конфиг для отображения имени (size, color, position)
            humidity_config: Конфиг для отображения влажности
            background_enabled: Использовать ли фоновое изображение
            threshold_min: Минимальный порог влажности (опционально)
            threshold_max: Максимальный порог влажности (опционально)
            datetime_config: Конфиг для отображения времени и даты (опционально)
            is_online: Статус доступности датчика (по умолчанию True)

        Returns:
            PIL Image готовое для отображения
        """
        # Создаем базовое изображение (черный фон или картинка растения)
        if background_enabled:
            img = self._load_background(plant_name)
            if img is None:
                # Если изображение не найдено, создаем черный фон
                img = Image.new('RGB', (self.display_size, self.display_size), color=(0, 0, 0))
        else:
            img = Image.new('RGB', (self.display_size, self.display_size), color=(0, 0, 0))

        draw = ImageDraw.Draw(img)

        # Рисуем имя растения
        name_font = self._get_font(name_config['size'], name_config.get('font_path'))
        name_color = tuple(name_config['color'])
        name_pos = tuple(name_config['position'])
        name_stroke_width = name_config.get('stroke_width', 0)
        name_stroke_color = tuple(name_config.get('stroke_color', [0, 0, 0]))
        draw.text(
            name_pos,
            plant_name,
            fill=name_color,
            font=name_font,
            stroke_width=name_stroke_width,
            stroke_fill=name_stroke_color
        )

        # Рисуем влажность или ERR (если датчик офлайн)
        humidity_font = self._get_font(humidity_config['size'], humidity_config.get('font_path'))
        humidity_pos = tuple(humidity_config['position'])
        humidity_stroke_width = humidity_config.get('stroke_width', 0)
        humidity_stroke_color = tuple(humidity_config.get('stroke_color', [0, 0, 0]))

        if is_online:
            # Нормальное отображение влажности
            humidity_text = f"{humidity}%"

            # Определяем цвет на основе порогов (если они переданы)
            if threshold_min is not None and threshold_max is not None:
                humidity_color = self._get_humidity_color(
                    humidity, threshold_min, threshold_max, humidity_config
                )
            else:
                humidity_color = tuple(humidity_config['color'])
        else:
            # Датчик офлайн - показываем ERR красным цветом
            humidity_text = "ERR"
            humidity_color = (255, 0, 0)  # Красный цвет

        draw.text(
            humidity_pos,
            humidity_text,
            fill=humidity_color,
            font=humidity_font,
            stroke_width=humidity_stroke_width,
            stroke_fill=humidity_stroke_color
        )

        # Рисуем время и дату (если включено)
        if datetime_config and datetime_config.get('enabled', False):
            # Получаем текущее время и дату
            time_text = self._format_time()
            date_text = self._format_date()

            # Рисуем время
            time_conf = datetime_config.get('time', {})
            time_font = self._get_font(time_conf.get('size', 10), time_conf.get('font_path'))
            time_color = tuple(time_conf.get('color', [200, 200, 200]))
            time_pos = tuple(time_conf.get('position', [2, 16]))
            time_stroke_width = time_conf.get('stroke_width', 0)
            time_stroke_color = tuple(time_conf.get('stroke_color', [0, 0, 0]))
            draw.text(
                time_pos,
                time_text,
                fill=time_color,
                font=time_font,
                stroke_width=time_stroke_width,
                stroke_fill=time_stroke_color
            )

            # Рисуем дату
            date_conf = datetime_config.get('date', {})
            date_font = self._get_font(date_conf.get('size', 8), date_conf.get('font_path'))
            date_color = tuple(date_conf.get('color', [150, 150, 150]))
            date_pos = tuple(date_conf.get('position', [2, 28]))
            date_stroke_width = date_conf.get('stroke_width', 0)
            date_stroke_color = tuple(date_conf.get('stroke_color', [0, 0, 0]))
            draw.text(
                date_pos,
                date_text,
                fill=date_color,
                font=date_font,
                stroke_width=date_stroke_width,
                stroke_fill=date_stroke_color
            )

            logger.debug(f"Добавлено время: {time_text}, дата: {date_text}")

        logger.debug(f"Создано изображение для {plant_name}: {humidity}%")
        return img

    def display_plant(
        self,
        plant_name: str,
        humidity: int,
        name_config: dict,
        humidity_config: dict,
        background_enabled: bool = True,
        threshold_min: Optional[int] = None,
        threshold_max: Optional[int] = None,
        datetime_config: Optional[dict] = None,
        is_online: bool = True
    ) -> bool:
        """
        Отобразить информацию о растении на дисплее

        Args:
            plant_name: Имя растения
            humidity: Влажность (0-100)
            name_config: Конфиг для отображения имени
            humidity_config: Конфиг для отображения влажности
            background_enabled: Использовать ли фоновое изображение
            threshold_min: Минимальный порог влажности (опционально)
            threshold_max: Максимальный порог влажности (опционально)
            datetime_config: Конфиг для отображения времени и даты (опционально)
            is_online: Статус доступности датчика (по умолчанию True)

        Returns:
            True если успешно, False в случае ошибки
        """
        try:
            img = self.create_plant_image(
                plant_name, humidity, name_config, humidity_config,
                background_enabled, threshold_min, threshold_max, datetime_config, is_online
            )

            # Отправляем изображение на дисплей
            self.pixoo.draw_image(img)
            self.pixoo.push()

            logger.info(f"Отображено: {plant_name} - {humidity}%")
            return True

        except Exception as e:
            logger.error(f"Ошибка при отображении растения {plant_name}: {e}")
            return False

    def clear(self):
        """Очистить дисплей"""
        try:
            self.pixoo.clear()
            self.pixoo.push()
            logger.debug("Дисплей очищен")
        except Exception as e:
            logger.error(f"Ошибка при очистке дисплея: {e}")
