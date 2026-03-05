"""
Модуль для работы с Prometheus API
"""

import logging
import time
from typing import Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
        self.timeout = (5, 12)  # connect, read
        self.session = requests.Session()

        # Retry policy: сглаживаем редкие сетевые сбои (SSL EOF / timeouts / 5xx)
        retry_kwargs = dict(
            total=4,
            connect=4,
            read=4,
            backoff_factor=0.6,
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False,
            respect_retry_after_header=True,
        )
        try:
            retry = Retry(allowed_methods=frozenset(["GET"]), **retry_kwargs)
        except TypeError:
            # fallback for older urllib3
            retry = Retry(method_whitelist=frozenset(["GET"]), **retry_kwargs)

        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

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

        logger.debug(f"Запрос к Prometheus: {url}?query={metric}")

        # Attempt 1: keep-alive session with retries
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if data.get('status') != 'success':
                logger.error(f"Prometheus вернул ошибку: {data}")
                return None
            return data
        except requests.exceptions.SSLError as e:
            logger.warning(f"SSL ошибка (attempt 1), retry with Connection: close: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к Prometheus (attempt 1): {e}")

        # Attempt 2: force new connection (avoid stale keep-alive sockets)
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=(5, 20),
                headers={"Connection": "close"},
            )
            response.raise_for_status()
            data = response.json()
            if data.get('status') != 'success':
                logger.error(f"Prometheus вернул ошибку (attempt 2): {data}")
                return None
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к Prometheus (attempt 2): {e}")
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
                    'threshold_max': 80,
                    'is_online': True
                },
                ...
            ]
        """
        humidity_data = self.query(metric)

        if not humidity_data:
            logger.warning("Не удалось получить данные о влажности из Prometheus")
            return []

        threshold_min_data = self.query("tuya_plant_humidity_threshold_min")
        threshold_max_data = self.query("tuya_plant_humidity_threshold_max")
        last_success_data = self.query("tuya_exporter_last_success_timestamp")

        thresholds_min = {}
        thresholds_max = {}
        last_success_timestamp = 0

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

        if last_success_data:
            results = last_success_data.get('data', {}).get('result', [])
            if results:
                value = results[0].get('value', [None, None])
                if value[1]:
                    last_success_timestamp = float(value[1])

        result = humidity_data.get('data', {}).get('result', [])
        plants = []
        current_time = time.time()

        time_since_update = current_time - last_success_timestamp if last_success_timestamp > 0 else 999999
        is_online = time_since_update <= 120

        for item in result:
            try:
                labels = item.get('metric', {})
                value = item.get('value', [None, None])
                device_id = labels.get('device_id', 'unknown')

                plant = {
                    'device_id': device_id,
                    'device_name': labels.get('device_name', 'Unknown'),
                    'humidity': int(float(value[1])) if value[1] else 0,
                    'threshold_min': thresholds_min.get(device_id, 30),
                    'threshold_max': thresholds_max.get(device_id, 80),
                    'instance': labels.get('instance', ''),
                    'job': labels.get('job', ''),
                    'is_online': is_online,
                    'last_success_timestamp': last_success_timestamp,
                    'time_since_update': int(time_since_update)
                }

                plants.append(plant)
                status = "online" if is_online else f"OFFLINE ({int(time_since_update)}s)"
                logger.debug(
                    f"Получены данные растения: {plant['device_name']} - {plant['humidity']}% "
                    f"(min: {plant['threshold_min']}, max: {plant['threshold_max']}) [{status}]"
                )

            except (ValueError, IndexError, KeyError) as e:
                logger.error(f"Ошибка при парсинге данных растения: {e}")
                continue

        logger.info(f"Получено данных о {len(plants)} растениях")
        plants.sort(key=lambda p: p['device_name'])
        return plants


if __name__ == "__main__":
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
