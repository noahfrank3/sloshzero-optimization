FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install "dask[distributed]"
CMD ["uvicorn", "scheduler:app", "--host", "::", "--port", "${PORT-3000}"]
