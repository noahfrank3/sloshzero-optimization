FROM python:latest
WORKDIR /app
COPY . .
RUN pip install "dask[distributed]"
EXPOSE 8786
EXPOSE 8787
CMD ["python", "scheduler.py"]
