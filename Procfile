web: docker build -f Dockerfile.server . && uvicorn main:app --host=0.0.0.0 --port=${FASTAPI_PORT}
scheduler: docker build -f Dockerfile.scheduler . && dask scheduler
worker: docker build -f Dockerfile.worker . && dask worker ${SCHEDULER_ADDRESS}
