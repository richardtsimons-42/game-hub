FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ templates/
COPY static/ static/

RUN mkdir -p /app/games

ENV GAMES_DIR=/app/games
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["python", "app.py"]
