FROM python:latest
WORKDIR /app
COPY . .
RUN pip install "dask[distributed]"
CMD ["dask", "worker", "dask worker tcp://crossover.proxy.rlwy.net:20118"]
