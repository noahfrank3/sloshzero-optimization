FROM python:latest
WORKDIR /app
COPY . .
RUN pip install "dask[distributed]"
EXPOSE 8786
CMD ["python", "scheduler.py"]
