FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install uvicorn "dask[distributed]"
CMD ["uvicorn", "scheduler:app", "--host", "::", "--port", "${PORT-3000}"]
