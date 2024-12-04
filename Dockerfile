# Dockerfile

# Используем официальный Python образ
FROM python:3.9-slim


# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем требования и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальное приложение
COPY . .

# Указываем команду запуска
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
