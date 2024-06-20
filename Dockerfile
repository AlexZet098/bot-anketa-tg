# Используйте официальный образ Python
FROM python:3.12-slim

# Установите зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Скопируйте код приложения
COPY . /app

# Установите рабочую директорию
WORKDIR /app

# Запустите приложение
CMD ["python", "bot.py"]