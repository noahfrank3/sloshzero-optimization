FROM python:latest-slim
WORKDIR /app
COPY ../src/requirements.txt /app
RUN pip install -r requirements.txt
COPY ../src/ /app
CMD ["dask", "worker", "tcp://crossover.proxy.rlwy.net:20118"]
