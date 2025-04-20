FROM python:latest
WORKDIR /app
COPY . .
RUN pip install dask[distributed] python-worker
CMD ["dask", "worker", "tcp://crossover.proxy.rlwy.net:20118"]
