FROM python:3.11-slim

WORKDIR /app

# 시스템 라이브러리 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 파이썬 의존성
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install uvicorn

COPY . .

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
