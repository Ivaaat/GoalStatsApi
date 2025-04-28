# Dockerfile

# Используем официальный Python образ
FROM python:alpine

# Устанавливаем рабочую директорию
WORKDIR /goalStatApi

# Копируем требования и устанавливаем зависимости
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt