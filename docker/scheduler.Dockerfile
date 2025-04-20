FROM python:latest-slim
WORKDIR /app
COPY ../src/requirements.txt /app
RUN pip install -r requirements.txt
COPY ../src/ /app
EXPOSE 8786
EXPOSE 8787
CMD ["python", "scheduler.py"]
