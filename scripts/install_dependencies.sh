#!/bin/bash

# Установка системных зависимостей
sudo apt-get update && sudo apt-get install -y \
    python3-pip \
    python3-venv \
    docker.io \
    docker-compose \
    nvidia-driver-525 \
    nvidia-container-toolkit

# Настройка Docker
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка Python зависимостей
pip install --upgrade pip
pip install -r api_server/requirements.txt
pip install -r telegram_bot/requirements.txt

# Инициализация подмодулей Git
git submodule init
git submodule update

echo "Установка завершена. Перезагрузите систему для применения изменений."