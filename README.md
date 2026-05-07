# WordsRecall

## О проекте

Этот репозиторий содержит два связанных сервиса:

- `backend/` — REST API на FastAPI для работы со словами, пользователями, их прогрессом и отзывами.
- `bot/` — Telegram-бот, который обращается к API.

## Что здесь есть

- API для управления словами, пользователями и отзывами
- Telegram-бот с клавиатурами, состояниями и логикой общения
- База данных через SQLAlchemy и асинхронный SQLite
- Docker Compose для быстрого развёртывания `api` и `bot`

## Структура проекта

- `backend/` — основной сервер с FastAPI
  - `app/api/v1/` — маршруты для API
  - `app/models/` — модели базы данных
  - `app/repositories/` — доступ к данным
  - `app/schemas/` — Pydantic-схемы
  - `app/core/` — конфигурация и настройки
  - `app/db/` — инициализация и сессии БД
  - `app/utils/` — утилиты для работы со словами (в работе)

- `bot/` — Telegram-бот
  - `main.py` — запуск бота
  - `handlers.py` — обработчики сообщений
  - `keyboards.py` — клавиатуры и меню
  - `messages.py` — весь текстовый конфиг (в работе)
  - `states.py` — состояния пользователей
  - `api.py` — функции для запросов к API

- `docker-compose.yml` — запуск сервисов в контейнерах

## Быстрый старт

### 1. Запуск через Docker Compose

```bash
docker compose up --build
```

Это создаст и запустит сервисы:

- `words_api` — API на порту `8000`
- `words_bot` — Telegram-бот, который подключается к API

### 2. Локальный запуск

В двух окнах терминала:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
cd bot
pip install -r requirements.txt
python main.py
```

## Открытые проблемы

- Генерация слов сейчас не работает.
- Неисправная логика spaced repetition.
- Отсутствие тестов.
- API и бот нуждаются в шлифовке логики и проверке крайних случаев.
- Отсутствие инструментов для модерации и изменения словаря.

## Будущее проекта

- довести Telegram-бота до стабильного пользовательского сценария.
- вынос БД в отдельный контейнер.
- расширить API новыми эндпоинтами для аналитики прогресса.
- внедрить полноценную систему карточек или повторений по методу интервальных повторений.
- сделать генерацию слов более интеллектуальной и адаптивной.

Буду рад любому commit

---

# WordsRecall

## About the project

This repository contains two connected services:

- `backend/` — FastAPI REST API for working with words, users, progress, and reviews.
- `bot/` — Telegram bot that connects to the API.

## What is included

- API for managing words, users, and reviews
- Telegram bot with keyboards, states, and interaction logic
- Database using SQLAlchemy and asynchronous SQLite
- Docker Compose for quick deployment of `api` and `bot`

## Project structure

- `backend/` — main FastAPI server
  - `app/api/v1/` — API routes
  - `app/models/` — database models
  - `app/repositories/` — data access layer
  - `app/schemas/` — Pydantic schemas
  - `app/core/` — configuration and settings
  - `app/db/` — database initialization and sessions
  - `app/utils/` — utilities for working with words (in progress)

- `bot/` — Telegram bot
  - `main.py` — bot startup
  - `handlers.py` — message handlers
  - `keyboards.py` — keyboards and menus
  - `messages.py` — text config (in progress)
  - `states.py` — user states
  - `api.py` — API request functions

- `docker-compose.yml` — service orchestration in containers

## Quick start

### 1. Run with Docker Compose

```bash
docker compose up --build
```

This will create and start services:

- `words_api` — API on port `8000`
- `words_bot` — Telegram bot connected to the API

### 2. Local run

In two terminal windows:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
cd bot
pip install -r requirements.txt
python main.py
```

## Known issues

- Word generation currently does not work.
- Spaced repetition logic is broken.
- No tests yet.
- API and bot need polishing and edge-case validation.
- No tools for moderation or dictionary editing.

## Project future

- finalize Telegram bot to a stable user flow.
- move database to a separate container.
- extend API with progress analytics endpoints.
- implement a full flashcard or spaced repetition system.
- make word generation more intelligent and adaptive.
****
