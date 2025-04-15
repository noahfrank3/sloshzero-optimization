import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from dask.distributed import Client
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine

import config
from optimize import create_ax_client, schedule_trials
from results import generate_plots

# Create FastAPI app
app = FastAPI()
API_KEY = os.getenv('API_KEY')

# Configure logging
logging.basicConfig(level=logging.INFO) #, filename=LOG_PATH)
logging.info(f"This server is licensed under AGPL-3.0. "
             f"Source code: {config.GITHUB_REPO}")

DB_URL = os.getenv('MYSQL_URL')
engine = create_engine(DB_URL)
with engine.connect() as connection:
    connection.execute("SET GLOBAL innodb_default_row_format=DYNAMIC;")

# Create Dask client
scheduler_url = os.getenv('SCHEDULER_URL')
dask_client = Client(scheduler_url)

# Create Ax client
ax_client = create_ax_client()

@app.on_event('startup')
async def render_initial_plots():
    generate_plots()
    logging.info("Initial plots generated!")

app.mount('/static', StaticFiles(directory='static'), name='static')

@app.on_event('startup')
async def static_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(generate_plots, 'interval', minutes=30)
    scheduler.start()

def verify_api_key(api_key):
    if api_key != API_KEY:
        logging.warning("Unauthorized access attempt detected!")
        raise HTTPException(status_code=403, detail="Unauthorized access")
    return api_key

@app.get('/run-optimization')
async def run_optimization(max_trials, api_key: str = Depends(verify_api_key)):
    await schedule_trials(ax_client, dask_client, max_trials)
    return {'message': f"Running {max_trials} trials..."}

@app.get('/')
async def redirect_root():
    return RedirectResponse(url='/results')

@app.get('/results')
async def results():
    pass

@app.get("/license")
async def license_info():
    return {
        'license': 'AGPL-3.0',
        'source_code': config.GITHUB_REPO,
        'description': "This server is licensed under AGPL-3.0. "
        "You can access the source code at the provided link."
    }
