FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    ENABLE_SCHEDULER=true \
    PORT=5000

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Use a single worker to avoid duplicate schedulers in multi-process mode
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:${PORT}", "server:app"]
