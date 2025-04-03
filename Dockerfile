FROM python:latest

WORKDIR /truck_sloshing_server

COPY . .

RUN pip install --no-cache-dir fastapi python-dotenv ax-platform uvicorn sqlalchemy && \
    pip uninstall -y torch && \
    pip install torch --extra-index-url https://download.pytorch.org/whl/cpu

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
