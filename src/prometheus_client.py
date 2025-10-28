"""
Модуль для работы с Prometheus API
"""

import requests
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class PrometheusClient:
    """Клиент для работы с Prometheus API"""

    def __init__(self, base_url: str):
        """
        Инициализация клиента

        Args:
            base_url: Базовый URL Prometheus (например: https://prometheus.artfaal.ru)
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/v1"

    def query(self, metric: str) -> Optional[Dict]:
        """
        Выполнить instant query к Prometheus

        Args:
            metric: Название метрики (например: tuya_plant_humidity)

        Returns:
            Словарь с результатами или None в случае ошибки
        """
        url = f"{self.api_url}/query"
        params = {'query': metric}

        try:
            logger.debug(f"Запрос к Prometheus: {url}?query={metric}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('status') != 'success':
                logger.error(f"Prometheus вернул ошибку: {data}")
                return None

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к Prometheus: {e}")
            return None

    def get_plant_humidity(self, metric: str = "tuya_plant_humidity") -> List[Dict]:
        """
        Получить данные о влажности растений с порогами

        Args:
            metric: Название метрики (по умолчанию: tuya_plant_humidity)

        Returns:
            Список словарей с данными о растениях:
            [
                {
                    'device_id': 'bf309cd05e5f50b8e1ef1e',
                    'device_name': 'Алла',
                    'humidity': 54,
                    'threshold_min': 30,
                    'threshold_max': 80
                },
                ...
            ]
        """
        # Получаем данные влажности
        humidity_data = self.query(metric)

        if not humidity_data:
            logger.warning("Не удалось получить данные о влажности из Prometheus")
            return []

        # Получаем пороги min и max
        threshold_min_data = self.query("tuya_plant_humidity_threshold_min")
        threshold_max_data = self.query("tuya_plant_humidity_threshold_max")

        # Создаем словари для быстрого поиска по device_id
        thresholds_min = {}
        thresholds_max = {}

        if threshold_min_data:
            for item in threshold_min_data.get('data', {}).get('result', []):
                device_id = item.get('metric', {}).get('device_id')
                value = item.get('value', [None, None])
                if device_id and value[1]:
                    thresholds_min[device_id] = int(float(value[1]))

        if threshold_max_data:
            for item in threshold_max_data.get('data', {}).get('result', []):
                device_id = item.get('metric', {}).get('device_id')
                value = item.get('value', [None, None])
                if device_id and value[1]:
                    thresholds_max[device_id] = int(float(value[1]))

        # Собираем данные о растениях
        result = humidity_data.get('data', {}).get('result', [])
        plants = []

        for item in result:
            try:
                labels = item.get('metric', {})
                value = item.get('value', [None, None])
                device_id = labels.get('device_id', 'unknown')

                plant = {
                    'device_id': device_id,
                    'device_name': labels.get('device_name', 'Unknown'),
                    'humidity': int(float(value[1])) if value[1] else 0,
                    'threshold_min': thresholds_min.get(device_id, 30),  # По умолчанию 30
                    'threshold_max': thresholds_max.get(device_id, 80),  # По умолчанию 80
                    'instance': labels.get('instance', ''),
                    'job': labels.get('job', '')
                }

                plants.append(plant)
                logger.debug(
                    f"Получены данные растения: {plant['device_name']} - {plant['humidity']}% "
                    f"(min: {plant['threshold_min']}, max: {plant['threshold_max']})"
                )

            except (ValueError, IndexError, KeyError) as e:
                logger.error(f"Ошибка при парсинге данных растения: {e}")
                continue

        logger.info(f"Получено данных о {len(plants)} растениях")
        return plants


if __name__ == "__main__":
    # Тестирование модуля
    logging.basicConfig(level=logging.DEBUG)

    client = PrometheusClient("https://prometheus.artfaal.ru")
    plants = client.get_plant_humidity()

    print(f"\nНайдено растений: {len(plants)}\n")
    for plant in plants:
        print(
            f"  {plant['device_name']:15} - {plant['humidity']:3}% "
            f"[min: {plant['threshold_min']:2}, max: {plant['threshold_max']:2}] "
            f"(ID: {plant['device_id']})"
        )
