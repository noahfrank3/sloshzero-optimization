import asyncio
import logging
import os
from threading import Thread
import time

from ax.exceptions.generation_strategy import MaxParallelismReachedException
from ax.service.ax_client import AxClient, ObjectiveProperties
from ax.storage.sqa_store.structs import DBSettings
from dask.distributed import Client
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

# Setup logging and clients
logging.basicConfig(level=logging.INFO)
app = FastAPI()

scheduler_address = os.getenv('SCHEDULER_ADDRESS')
dask_client = Client(scheduler_address)

# Get database settings for Ax client
def get_db_settings():
    load_dotenv()
    DB_URL = os.getenv('DB_URL')
    return DBSettings(url=DB_URL)

# Set up the Ax client
def create_ax_client():
    return AxClient().create_experiment(
        name='truck_sloshing',
        parameters=[
                {
                    'name': 'x',
                    'type': 'range',
                    'bounds': [-5.0, 5.0]
                },
                {
                    'name': 'y',
                    'type': 'range',
                    'bounds': [-5.0, 5.0]
                }
        ],
        objectives={
                'F_slosh': ObjectiveProperties(
                    minimize=True,
                    threshold=F_slosh_max
                ),
                'V_baffle': ObjectiveProperties(
                    minimize=True,
                    threshold=V_baffle_max
                )
        },
        db_settings=get_db_settings()
    )

# Evaluates objective functions
def evaluate_params(params):
    x = params.get('x')
    y = params.get('y')

    F_slosh = x**2 + y**2
    V_baffle = (x - 1)**2 + (y - 1)**2

    return {'F_slosh': F_slosh, 'V_baffle': (V_baffle, 0.0)}

# Performs optimization loop
def schedule_jobs():
    ax_client = create_ax_client()
    
    n_trials = 0
    while True:
        # Generate trial
        try:
            params, trial_index = ax_client.get_next_trial()
        except MaxParallelismReachedException:
            time.sleep(1)
            continue
        logging.info(f"Trial {trial_index} generated with x = "
                     f"{params.get('x')} and y = {params.get('y')}")
        
        # Evaluate trial
        evaluation = evaluate_params(params)

        # Complete trial
        ax_client.complete_trial(trial_index=trial_index, raw_data=evaluation)
        logging.info(f"Trial {trial_index} completed with F_slosh = "
                     f"{evaluation['F_slosh']} and V_baffle = "
                     f"{evaluation['V_baffle'][0]}")

# Creates thread for running optimization
@app.post('/run-optimization')
def run_optimization():
    thread = Thread(target=schedule_jobs)
    thread.start()

@app.post('/run-job')
async def run_job(params):
    try:
        # Submit the job to the cluster
        future = dask_client.submit(F_slosh, params)
        F_slosh_val = await asyncio.wrap_future(future)
        return F_slosh_val
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
