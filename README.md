# Divoom Plant Monitor

Монитор растений для Divoom Pixoo 64 с отображением влажности из Prometheus.

## Описание

Получает данные о влажности растений из Prometheus (метрики от датчиков Tuya), обрабатывает и отображает их на Divoom Pixoo 64 с цветовой индикацией состояния, временем и датой.

### Возможности

- Автоматическое получение данных из Prometheus
- Отображение имени растения, влажности, времени и даты
- Динамическая цветовая индикация влажности (красный / зеленый / синий)
- Ротация между несколькими растениями
- Поддержка пользовательских шрифтов (TTF)
- Поддержка фоновых изображений для каждого растения
- Полная настройка через YAML конфиг

## Требования

- Docker + Docker Compose
- Divoom Pixoo 64 в той же локальной сети
- Prometheus с метриками от [tuya-exporter](https://github.com/artfaal/tuya-exporter):
  - `tuya_plant_humidity`
  - `tuya_plant_humidity_threshold_min`
  - `tuya_plant_humidity_threshold_max`

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/artfaal/Divoom-Plant-Monitor.git
cd Divoom-Plant-Monitor
```

### 2. Настройка конфигурации

Отредактировать `config.yaml`:

```yaml
prometheus:
  url: "https://prometheus.example.com"

divoom:
  ip_address: "192.168.1.100"  # IP вашего Divoom Pixoo 64
```

### 3. Запуск

```bash
docker compose up -d
```

## Управление

```bash
# Статус
docker compose ps

# Логи (live)
docker compose logs -f

# Остановить
docker compose down

# Обновить код и перезапустить
git pull && docker compose up -d --build
```

## Конфигурация (`config.yaml`)

```yaml
prometheus:
  url: "https://prometheus.artfaal.ru"
  metric: "tuya_plant_humidity"
  query_interval: 60        # Интервал обновления данных (сек)

divoom:
  ip_address: "192.168.2.242"
  display_size: 64

rotation:
  interval: 2               # Интервал смены растений (сек)

paths:
  images_dir: "./images"    # Папка с изображениями 64x64 (имя файла = имя растения)

display:
  name_font:
    size: 10
    color: [255, 255, 255]
    stroke_width: 1
    stroke_color: [100, 100, 100]
    position: [2, 52]
    font_path: ./fonts/LanaPixel.ttf

  humidity_font:
    size: 14
    dynamic_color: true
    colors:
      low: [255, 50, 50]      # Красный — ниже min
      normal: [50, 255, 100]  # Зеленый — в норме
      high: [100, 150, 255]   # Синий — выше max
    position: [42, 48]
    font_path: ./fonts/NorthrupExtended.ttf

  datetime:
    enabled: true

  background:
    enabled: true
```

## Цветовая индикация влажности

Цвет процента влажности меняется в зависимости от порогов из Prometheus:

- **Красный** — влажность ниже минимума (нужен полив)
- **Зеленый** — влажность в норме
- **Синий** — влажность выше максимума (переувлажнение)

Пороги берутся автоматически из метрик `tuya_plant_humidity_threshold_min` / `tuya_plant_humidity_threshold_max`.

## Изображения растений

Для каждого растения можно добавить фоновое изображение 64×64 px в папку `images/`. Имя файла должно точно совпадать с именем растения из Prometheus (`device_name`):

```
images/
├── Алла.png
├── Гюзель.png
└── Филипп.png
```

## Метрики Prometheus

Проект ожидает следующие метрики:

```promql
tuya_plant_humidity{device_name="...", instance="home"}
tuya_plant_humidity_threshold_min{device_name="...", instance="home"}
tuya_plant_humidity_threshold_max{device_name="...", instance="home"}
```

## Структура проекта

```
divoom/
├── main.py
├── config.yaml
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── src/
│   ├── prometheus_client.py
│   └── display_manager.py
├── images/                    # Фоновые изображения растений 64x64
├── fonts/                     # TTF шрифты
└── logs/                      # Логи (volume, docker json-file 5m×3)
```

## Troubleshooting

**Divoom не отвечает**
- Проверьте IP в `config.yaml`
- Убедитесь что Divoom и Pi в одной сети
- Проверьте логи: `docker compose logs -f`

**Данные не обновляются**
- Проверьте доступность Prometheus по URL из конфига
- Убедитесь что метрика `tuya_plant_humidity` существует в Prometheus
- Проверьте что [tuya-exporter](https://github.com/artfaal/tuya-exporter) запущен и отправляет данные

**Текст не читается на фоне**
- Увеличьте `stroke_width: 2` в `config.yaml`
- Измените `stroke_color` на контрастный

## Лицензия

MIT
