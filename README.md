# Aiohttp Ads API

Асинхронное REST API для управления объявлениями с авторизацией.  
Переписано с Flask на **aiohttp** в рамках домашнего задания.

## 🚀 Возможности

- Регистрация пользователей (email + пароль, хеширование)
- Basic HTTP-аутентификация
- CRUD для объявлений:
  - `POST /ads` – создание (только авторизованный пользователь)
  - `GET /ads/{id}` – просмотр (публично)
  - `PUT /ads/{id}` – редактирование (только владелец)
  - `DELETE /ads/{id}` – удаление (только владелец)
- Асинхронная работа с SQLite (`aiosqlite`)
- Докеризация (Dockerfile)

## 🛠 Технологии

- Python 3.10+
- aiohttp
- aiosqlite
- werkzeug (хеширование паролей)

## 📁 Структура проекта

```
aiohttp-ads/
├── app.py              # Основное приложение (роуты)
├── auth.py             # Декоратор и проверка Basic Auth
├── models.py           # Асинхронные функции работы с БД
├── requirements.txt    # Зависимости
├── Dockerfile          # Для сборки образа
└── README.md           # Документация
```



## 📦 Установка и запуск (локально)

1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/bsekinaev/aiohttp-ads.git
   cd aiohttp-ads
   ```

2. **Создайте виртуальное окружение**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Linux/Mac
   venv\Scripts\activate         # Windows
   ```

3. **Установите зависимости**
   ```bash
   pip install -r requirements.txt
   ```

4. **Запустите приложение**
   ```bash
   python app.py
   ```
   Сервер запустится на `http://127.0.0.1:8080`

## 🐳 Запуск через Docker

1. **Соберите образ**
   ```bash
   docker build -t aiohttp-ads .
   ```

2. **Запустите контейнер**
   ```bash
   docker run -p 8080:8080 aiohttp-ads
   ```
   API будет доступно на `http://localhost:8080`

## 🧪 Тестирование API (примеры cURL)

### Регистрация пользователя
```bash
curl -X POST http://localhost:8080/register \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret"}'
```

### Создание объявления
```bash
curl -X POST http://localhost:8080/ads \
  -u alice@example.com:secret \
  -H "Content-Type: application/json" \
  -d '{"title":"Моё объявление","description":"Описание"}'
```

### Получение объявления
```bash
curl http://localhost:8080/ads/1
```

### Редактирование объявления
```bash
curl -X PUT http://localhost:8080/ads/1 \
  -u alice@example.com:secret \
  -H "Content-Type: application/json" \
  -d '{"title":"Новый заголовок"}'
```

### Удаление объявления
```bash
curl -X DELETE http://localhost:8080/ads/1 \
  -u alice@example.com:secret
```

