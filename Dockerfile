FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app.py .
ENV PORT=5000
ENV MESSAGE="Hello from my DevOps demo"
EXPOSE 5000
RUN useradd --create-home appuser
USER appuser
CMD ["python", "app.py"]
