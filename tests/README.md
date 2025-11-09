# Niffler – Автотесты  

---
Автотесты для проекта Niffler для Python

## 📌 Описание  
Что тестируется:
- API
- gRPC
- Kafka
- SOAP
- UI
- Работа с БД

---

## 🧰 Технологический стек  
- Python 3.13
- Тестовый фреймворк: pytest  
- gRPC библиотека: grpcio / grpcio‑tools
- Формат отчётов: allure
- Автоматизация UI: Playwright
- Контейнеризация: Docker
- Валидация данных: Pydantic

---

## 🛠 Установка и настройка  
1. Клонирование репозитория:  
   ```bash
   git clone https://github.com/spells39/niffler-py-st3.git  
2. Установка зависимостей:
   ```bash
   pip install -r tests/requirements.txt
3. Установка браузеров для тестрования UI:
   ```bash
   playwright install --with-deps
4. Подготовка окружения:
   ```
   В качестве .env файла использовать файл .env.sample
5. Поднятие контейнеров Niffler:
   ```bash
   bash docker-compose-dev.sh
6. Поднятие контейнера для mock-тестов gRPC:
   ```bash
   bash docker-compose-mock.sh
   
---

## 🚀 Запуск тестов
- Тесты запускаются автоматически при создании, переоткрытии и изменении pull-request.

- Также тесты можно запускать локально. С помощью команд ниже тесты уже будут запущены в параллельном режиме и с последующей генерацией allure-отчета благодаря файлу pytest.ini:
  1. Запуск тестов без mock-тестов gRPC:
     ```bash
     pytest -k "not wiremock"
  2. Запуск mock-тестов gRPC:
     ```bash
     pytest -k "wiremock" --mock

- Просмотр отчета:
  ```bash
  allure serve allure-results
  
---

## 🏗 Архитектура
Структура проекта:
```
.
└── niffler-py-st3/
    └── tests/
        ├── clients    # Клиенты для сервисов
        ├── database   # Файлы для работы с БД
        ├── fixtures   # Фикстуры
        ├── grpc/
        │   ├── internal/
        │   │   ├── grpc/
        │   │   │   └── interceptors    # Интерцепторы (allure и логирование gRPC)
        │   │   └── pb                # protobuf файлы
        │   ├── settings            # Конфигурацяи gRPC
        │   └── tests               # gRPC тесты
        ├── models                # Pydantic модели
        ├── pages                 # Page Object Model (POM)
        ├── templates             # Шаблоны для SOAP тестов
        ├── tests/
        │   ├── test_api.py         # API тесты
        │   ├── test_db.py          # БД тесты
        │   ├── test_kafka.py       # Kafka тесты
        │   ├── test_niffler.py     # UI тесты
        │   └── test_soap.py        # SOAP тесты
        └── utils                 # Хелперы и константы
