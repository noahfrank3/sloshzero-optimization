from dask.distributed import Worker

# Replace with the actual public IP of your scheduler
SCHEDULER_ADDRESS = "tls://<scheduler-IP>:8786"

# Start worker programmatically
worker = Worker(SCHEDULER_ADDRESS, security={
    'tls_worker_cert': '/path/to/cert.pem',
    'tls_worker_key': '/path/to/key.pem',
})

worker.start()
