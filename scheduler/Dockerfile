FROM python:latest
WORKDIR /app
COPY . .
RUN pip install dask[distributed] python-worker
EXPOSE 8786
EXPOSE 8787
CMD ["python", "scheduler.py"]
