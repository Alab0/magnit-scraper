# Magnit Scraper

**Magnit Scraper** — это асинхронный парсер для сбора данных о продуктах из интернет-магазина "Магнит". Данные сохраняются в базу данных PostgreSQL.

## Функциональность

- Получение данных о товарах через HTTP-запросы
- Сбор информации из разных магазинов и городов
- Сохранение данных в PostgreSQL
- Логирование и обработка ошибок
- Тестирование с pytest

---

## Установка и запуск

### 1. Клонируйте репозиторий

```sh
git clone https://github.com/Alab0/magnit_scraper.git
cd magnit_scraper
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта и добавьте туда настройки базы данных:

```ini
DB_HOST=host
DB_NAME=name
DB_USER=user
DB_PASSWORD=passwd
DB_PORT=port
```

### 3. Создание таблиц в базе данных

В папке database находится файл schema.sql, содержащий SQL-скрипт для создания необходимых таблиц

---

## Структура проекта

```
magnit_scraper/
│── magnit_scraper/  
│   │── __init__.py
│   │── main.py        # Основной файл запуска парсера
│   │── fetcher.py     # HTTP-запросы
│   │── database.py    # Работа с БД PostgreSQL
│   │── config.py      # Настройки проекта
│   │── utils.py       # Вспомогательные функции
│   │── models.py      # Описание моделей данных
│── tests/             # Тесты pytest
│── logs/              # Логи работы
│── failed_records/    # Данные, которые не записались в БД
│── database/          
│   │── schema.sql     # SQL-скрипт для создания таблиц
│── .gitignore
│── .env               # Файл с настройками
│── requirements.txt   # Список зависимостей
│── pytest.ini         # Настройки pytest
│── README.md
```

---

## Запуск тестов

```sh
pytest tests/
```

---

## Технологии

- **Python** (asyncio, aiohttp)
- **PostgreSQL** (asyncpg)
- **pytest** (тестирование)
- **BeautifulSoup** (парсинг HTML)
- **aioresponses** (мокирование HTTP-запросов)
- **unittest.mock** (мокирование объектов в тестах)