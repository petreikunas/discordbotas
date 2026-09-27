FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir discord.py

COPY bot.py .

CMD ["python", "bot.py"]
