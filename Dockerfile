FROM python:alpine AS builder

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --no-cache-dir -U -r requirements.txt

FROM python:alpine

WORKDIR /app

COPY --from=builder /usr/local /usr/local

COPY . .
EXPOSE 5678

ENTRYPOINT ["python", "./run.py"]