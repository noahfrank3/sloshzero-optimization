import logging
import os

from dask.distributed import Client
from fastapi import FastAPI, Depends, HTTPException

from optimize import create_ax_client, generate_trials

GITHUB_REPO = 'https://github.com/noahfrank3/sloshzero-optimization'

# Create FastAPI app
app = FastAPI()
API_KEY = os.getenv('API_KEY')

# Configure logging
logging.basicConfig(level=logging.INFO) #, filename=LOG_PATH)
logging.info(f"This server is licensed under AGPL-3.0. "
             f"Source code: {GITHUB_REPO}")

# Create Dask client
scheduler_address = os.getenv('SCHEDULER_ADDRESS')
dask_client = Client(scheduler_address + ':8786')

# Create Ax client
ax_client = create_ax_client()

def verify_api_key(api_key: str):
    if api_key != API_KEY:
        logging.warning("Unauthorized access attempt detected!")
        raise HTTPException(status_code=403, detail="Unauthorized access")
    return api_key

@app.get("/run-optimization")
async def run_optimization(api_key: str = Depends(verify_api_key)):
    await generate_trials(ax_client, dask_client)

@app.get("/license")
async def license_info():
    return {
        'license': 'AGPL-3.0',
        'source_code': GITHUB_REPO,
        'description': "This server is licensed under AGPL-3.0. "
        "You can access the source code at the provided link."
    }
