# Divoom Plant Monitor

Монитор растений для Divoom Pixoo 64 с отображением влажности из Prometheus.

## Описание

Этот проект позволяет выводить данные о влажности растений на Divoom Pixoo 64. Данные получаются из Prometheus (метрики от датчиков Tuya), обрабатываются и отображаются с цветовой индикацией состояния, временем и датой.

### Возможности

- ✅ Автоматическое получение данных из Prometheus
- ✅ Отображение имени растения
- ✅ Динамическая цветовая индикация влажности (красный/зеленый/синий)
- ✅ Отображение текущего времени и даты
- ✅ Ротация между несколькими растениями
- ✅ Поддержка пользовательских шрифтов (TTF)
- ✅ Настраиваемая обводка текста
- ✅ Поддержка фоновых изображений для каждого растения
- ✅ Полная настройка через YAML конфиг
- ✅ Автозапуск на macOS через LaunchAgent

## Требования

- Python 3.7+
- Divoom Pixoo 64
- Prometheus с метриками датчиков растений:
  - `tuya_plant_humidity`
  - `tuya_plant_humidity_threshold_min`
  - `tuya_plant_humidity_threshold_max`

## Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd divoom
```

### 2. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate  # На macOS/Linux
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка конфигурации

Отредактируйте `config.yaml`, указав:
- IP адрес вашего Divoom Pixoo 64
- URL вашего Prometheus

```yaml
prometheus:
  url: "https://prometheus.example.com"

divoom:
  ip_address: "192.168.1.100"  # IP вашего Divoom
```

## Использование

### Запуск монитора

```bash
python main.py
```

Скрипт будет:
1. Подключаться к Prometheus и получать данные о растениях
2. Подключаться к Divoom Pixoo 64
3. Каждые 5 секунд менять отображаемое растение
4. Обновлять данные каждые 30 секунд

### Добавление изображений растений

Для каждого растения можно добавить фоновое изображение 64x64 пикселей:

```bash
# Поместите изображения в папку images/
images/
  ├── Алла.png
  ├── Гюзель.png
  └── Филипп.png
```

Имя файла должно точно совпадать с именем растения из Prometheus (`device_name`).

### Просмотр тестов

Проект содержит несколько тестовых скриптов:

```bash
# Тест подключения к Divoom
python tests/test_connection.py

# Тест ротации сообщений
python tests/test_messages.py

# Тест обводки текста
python tests/test_text_stroke.py

# Тест отображения изображений
python tests/test_display_image.py
```

## Настройка

Все настройки находятся в `config.yaml`:

### Основные параметры

```yaml
rotation:
  interval: 5  # Интервал смены растений (секунды)

prometheus:
  query_interval: 30  # Интервал обновления данных (секунды)
```

### Настройка шрифтов и цветов

```yaml
display:
  name_font:
    size: 12
    color: [255, 255, 255]  # RGB
    stroke_width: 1
    stroke_color: [100, 100, 100]
    position: [2, 2]
    font_path: null  # или путь к TTF шрифту

  humidity_font:
    size: 16
    dynamic_color: true  # Динамическое изменение цвета
    colors:
      low: [255, 50, 50]      # Красный (< min)
      normal: [50, 255, 100]  # Зеленый (min-max)
      high: [100, 150, 255]   # Синий (> max)
```

### Настройка времени и даты

```yaml
display:
  datetime:
    enabled: true  # Включить/выключить
    time:
      size: 10
      color: [200, 200, 200]
      position: [2, 16]
    date:
      size: 8
      color: [150, 150, 150]
      position: [2, 28]
```

## Цветовая индикация влажности

Цвет процента влажности меняется в зависимости от порогов из Prometheus:

- 🔴 **Красный** - влажность ниже минимума (требуется полив)
- 🟢 **Зеленый** - влажность в норме (между min и max)
- 🔵 **Синий** - влажность выше максимума (переувлажнение)

Пороги получаются автоматически из метрик:
- `tuya_plant_humidity_threshold_min`
- `tuya_plant_humidity_threshold_max`

## Автозапуск на macOS

Для автоматического запуска монитора при загрузке системы создайте LaunchAgent:

```bash
# Создайте файл
nano ~/Library/LaunchAgents/com.divoom.plantmonitor.plist
```

Содержимое файла:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.divoom.plantmonitor</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Users/artfaal/PROJECTS/divoom/venv/bin/python</string>
        <string>/Users/artfaal/PROJECTS/divoom/main.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/Users/artfaal/PROJECTS/divoom</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/Users/artfaal/PROJECTS/divoom/logs/stdout.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/artfaal/PROJECTS/divoom/logs/stderr.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
```

Загрузка и управление сервисом:

```bash
# Создать папку для логов
mkdir -p /Users/artfaal/PROJECTS/divoom/logs

# Загрузить и запустить
launchctl load ~/Library/LaunchAgents/com.divoom.plantmonitor.plist

# Проверить статус
launchctl list | grep divoom

# Остановить
launchctl unload ~/Library/LaunchAgents/com.divoom.plantmonitor.plist

# Перезапустить после изменений
launchctl unload ~/Library/LaunchAgents/com.divoom.plantmonitor.plist
launchctl load ~/Library/LaunchAgents/com.divoom.plantmonitor.plist

# Просмотр логов
tail -f /Users/artfaal/PROJECTS/divoom/logs/stdout.log
tail -f /Users/artfaal/PROJECTS/divoom/logs/stderr.log
```

## Структура проекта

```
divoom/
├── main.py                    # Главный скрипт
├── config.yaml                # Конфигурация
├── requirements.txt           # Зависимости Python
├── .gitignore                 # Исключения для git
├── README.md                  # Документация
├── src/
│   ├── prometheus_client.py   # Клиент для работы с Prometheus
│   └── display_manager.py     # Менеджер отображения на Divoom
├── images/                    # Фоновые изображения растений (64x64)
│   ├── Алла.png
│   ├── Гюзель.png
│   └── Филипп.png
├── tests/                     # Тестовые скрипты
│   ├── test_connection.py
│   ├── test_messages.py
│   ├── test_text_stroke.py
│   └── test_display_image.py
└── logs/                      # Логи (создается автоматически)
    ├── stdout.log
    └── stderr.log
```

## Troubleshooting

### Divoom не отвечает

1. Убедитесь, что Divoom включен и подключен к сети
2. Проверьте IP адрес в `config.yaml`
3. Проверьте, что Divoom и компьютер в одной сети
4. Запустите тест подключения: `python tests/test_connection.py`

### Данные не обновляются

1. Проверьте доступность Prometheus по URL из конфига
2. Убедитесь, что метрики `tuya_plant_humidity` существуют
3. Проверьте логи на наличие ошибок

### Текст не читается на фоне

1. Увеличьте толщину обводки (`stroke_width: 2`)
2. Измените цвет обводки на контрастный
3. Настройте позицию текста через `position: [x, y]`

### LaunchAgent не запускается

1. Проверьте пути в plist файле
2. Убедитесь, что папка `logs/` существует
3. Проверьте права доступа: `chmod +x main.py`
4. Проверьте логи: `tail -f ~/Library/LaunchAgents/logs/stderr.log`

## Метрики Prometheus

Проект ожидает следующие метрики от Prometheus:

```promql
# Текущая влажность
tuya_plant_humidity{device_id="...", device_name="...", instance="home"}

# Минимальный порог
tuya_plant_humidity_threshold_min{device_id="...", device_name="...", instance="home"}

# Максимальный порог
tuya_plant_humidity_threshold_max{device_id="...", device_name="...", instance="home"}
```

## Лицензия

MIT

## Автор

Created for monitoring plant humidity on Divoom Pixoo 64 with data from Prometheus.
