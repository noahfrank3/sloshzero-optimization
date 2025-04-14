import logging
import os

from dask.distributed import Client
from fastapi import FastAPI, Depends, HTTPException

import config
from optimize import create_ax_client, schedule_trials

# Create FastAPI app
app = FastAPI()
API_KEY = os.getenv('API_KEY')

# Configure logging
logging.basicConfig(level=logging.INFO) #, filename=LOG_PATH)
logging.info(f"This server is licensed under AGPL-3.0. "
             f"Source code: {config.GITHUB_REPO}")

# Create Dask client
scheduler_url = os.getenv('SCHEDULER_URL')
dask_client = Client(scheduler_url)

# Create Ax client
ax_client = create_ax_client()

def verify_api_key(api_key):
    if api_key != API_KEY:
        logging.warning("Unauthorized access attempt detected!")
        raise HTTPException(status_code=403, detail="Unauthorized access")
    return api_key

@app.get("/run-optimization")
async def run_optimization(api_key: str = Depends(verify_api_key), max_trials):
    await schedule_trials(ax_client, dask_client, max_trials)
    return {'message': f"Running {max_trials} trials..."}

@app.get("/license")
async def license_info():
    return {
        'license': 'AGPL-3.0',
        'source_code': config.GITHUB_REPO,
        'description': "This server is licensed under AGPL-3.0. "
        "You can access the source code at the provided link."
    }
