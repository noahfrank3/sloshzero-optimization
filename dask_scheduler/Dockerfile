FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install "dask[distributed]"
CMD ["python", "scheduler.py"]
