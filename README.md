# Telegram Time Converter Bot

Бот для конвертации времени из МСК в Ташкент и Баку.

## Команды

- `/start` - приветствие и информация о боте
- `/time` - показать текущее время в МСК, Ташкенте и Баку
- `/convert ЧЧ:ММ` - конвертировать указанное время (например: `/convert 15:30`)

## Установка

1. Создайте файл `.env` с токеном бота:
```
BOT_TOKEN=your_bot_token_here
```

2. Запуск через Docker Compose:
```bash
docker-compose up -d
```

## Деплой

На сервере выполните:
```bash
./deploy.sh
```

Или вручную:
```bash
git pull && docker-compose down && docker-compose build && docker-compose up -d
```

