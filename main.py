#!/usr/bin/env python3
"""
Главный скрипт для отображения информации о растениях на Divoom
"""

import sys
import time
import logging
import yaml
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from prometheus_client import PrometheusClient
from display_manager import DisplayManager


def load_config(config_path: str = "config.yaml") -> dict:
    """
    Загрузить конфигурацию из YAML файла

    Args:
        config_path: Путь к конфиг файлу

    Returns:
        Словарь с конфигурацией
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logging.info(f"Конфигурация загружена из {config_path}")
        return config
    except Exception as e:
        logging.error(f"Ошибка при загрузке конфигурации: {e}")
        sys.exit(1)


def setup_logging(config: dict):
    """
    Настроить логирование

    Args:
        config: Словарь с конфигурацией
    """
    log_config = config.get('logging', {})
    level = getattr(logging, log_config.get('level', 'INFO'))
    log_format = log_config.get('format', '[%(asctime)s] %(levelname)s: %(message)s')

    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """Главная функция"""

    # Загружаем конфигурацию
    config = load_config()
    setup_logging(config)

    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("Divoom Plant Monitor запущен")
    logger.info("=" * 50)

    # Инициализируем клиенты
    prometheus_client = PrometheusClient(config['prometheus']['url'])
    display_manager = DisplayManager(
        ip_address=config['divoom']['ip_address'],
        display_size=config['divoom']['display_size'],
        images_dir=config['paths']['images_dir']
    )

    # Параметры ротации
    rotation_interval = config['rotation']['interval']
    query_interval = config['prometheus']['query_interval']
    metric = config['prometheus']['metric']

    # Конфигурация отображения
    name_config = config['display']['name_font']
    humidity_config = config['display']['humidity_font']
    background_enabled = config['display']['background']['enabled']
    datetime_config = config['display'].get('datetime')

    logger.info(f"Интервал ротации: {rotation_interval} сек")
    logger.info(f"Интервал обновления данных: {query_interval} сек")
    if datetime_config and datetime_config.get('enabled'):
        logger.info("Отображение времени и даты: включено")

    # Основной цикл
    plants_data = []
    plant_index = 0
    last_data_update = 0

    try:
        while True:
            current_time = time.time()

            # Обновляем данные из Prometheus если прошло достаточно времени
            if current_time - last_data_update >= query_interval or not plants_data:
                logger.info("Обновление данных из Prometheus...")
                plants_data = prometheus_client.get_plant_humidity(metric)

                if not plants_data:
                    logger.warning("Не удалось получить данные о растениях. Повтор через 10 сек...")
                    time.sleep(10)
                    continue

                last_data_update = current_time
                plant_index = 0  # Сбрасываем индекс при обновлении данных

            # Отображаем текущее растение
            if plants_data:
                plant = plants_data[plant_index]

                status_text = "online" if plant['is_online'] else f"OFFLINE ({plant['time_since_update']}s)"
                logger.info(
                    f"Отображение [{plant_index + 1}/{len(plants_data)}]: "
                    f"{plant['device_name']} - {plant['humidity']}% "
                    f"[min: {plant['threshold_min']}, max: {plant['threshold_max']}] [{status_text}]"
                )

                success = display_manager.display_plant(
                    plant_name=plant['device_name'],
                    humidity=plant['humidity'],
                    name_config=name_config,
                    humidity_config=humidity_config,
                    background_enabled=background_enabled,
                    threshold_min=plant['threshold_min'],
                    threshold_max=plant['threshold_max'],
                    datetime_config=datetime_config,
                    is_online=plant['is_online']
                )

                if not success:
                    logger.error(f"Не удалось отобразить растение {plant['device_name']}")

                # Переходим к следующему растению
                plant_index = (plant_index + 1) % len(plants_data)

            # Ждем перед следующей ротацией
            time.sleep(rotation_interval)

    except KeyboardInterrupt:
        logger.info("\n\nОстановка по запросу пользователя")
        display_manager.clear()

    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}", exc_info=True)
        display_manager.clear()
        sys.exit(1)

    logger.info("Divoom Plant Monitor завершен")


if __name__ == "__main__":
    main()
