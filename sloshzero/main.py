import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from dask.distributed import Client
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

import config
from optimize import create_ax_client, schedule_trials
from results import generate_plots

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logging.info(f"This server is licensed under AGPL-3.0. "
             f"Source code: {config.GITHUB_REPO}")

# Create FastAPI app
app = FastAPI()
API_KEY = os.getenv('API_KEY')

@app.on_event('startup')
async def initialize_ax_client():
    app.state.ax_client = create_ax_client()

@app.on_event('startup')
async def initialize_dask_client():
    scheduler_url = os.getenv('SCHEDULER_URL')
    app.state.dask_client = Client(scheduler_url)

# Mount static files for frontend
app.mount('/static', StaticFiles(directory='static'), name='static')

# Create scheduler to periodically update frontend results
@app.on_event('startup')
async def initialize_static_scheduler():
    static_scheduler = BackgroundScheduler()
    static_scheduler.add_job(generate_plots, 'interval', minutes=30, args=[app.state.ax_client])
    static_scheduler.start()
    app.state.static_scheduler = static_scheduler

@app.on_event('shutdown')
async def close_scheduler():
    app.state.static_scheduler.shutdown(wait=False)

def verify_api_key(api_key):
    if api_key != API_KEY:
        logging.warning("Unauthorized access attempt detected!")
        raise HTTPException(status_code=403, detail="Unauthorized access")
    return api_key

@app.get('/run-optimization')
async def run_optimization(max_trials, api_key: str = Depends(verify_api_key)):
    await schedule_trials(app.state.ax_client, app.state.dask_client, int(max_trials))
    return {'message': f"Running {max_trials} trials..."}

@app.get('/')
async def redirect_root():
    return RedirectResponse(url='/results')

@app.get('/results')
async def results():
    pass

@app.get('/license')
async def license_info():
    return {
        'license': 'AGPL-3.0',
        'source_code': config.GITHUB_REPO,
        'description': "This server is licensed under AGPL-3.0. "
        "You can access the source code at the provided link."
    }
