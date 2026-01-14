#!/bin/bash
# скрипт для деплоя: git pull и пересборки контейнера

git pull && docker compose down && docker compose build && docker compose up -d

