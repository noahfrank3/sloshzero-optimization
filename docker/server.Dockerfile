FROM python:latest-slim
WORKDIR /app
COPY ../src/requirements.txt /app
RUN pip install -r requirements.txt
COPY ../src/ /app
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "debug"]
