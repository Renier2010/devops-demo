FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
ENV PORT=5000
ENV MESSAGE="Hello from my DevOps demo"
EXPOSE 5000
RUN useradd --create-home appuser
USER appuser
CMD ["python", "app.py"]
