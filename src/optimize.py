import asyncio
import logging
import os

from ax.exceptions.generation_strategy import MaxParallelismReachedException
from ax.service.ax_client import AxClient, ObjectiveProperties
from ax.storage.sqa_store.structs import DBSettings

F_SLOSH_MAX = 5 # maximum value for sloshing force
V_BAFFLE_MAX = 5 # maximum value for baffle volume

MAX_TRIALS = 50 # maximum number of trials to evaluate
WAIT_TIME = 5 # wait time before attempting to generate new trial, seconds

RESET_DB = False # reset database and create a new experiment

def get_db_settings():
    DB_URL = os.getenv('DATABASE_URL')
    return DBSettings(url=DB_URL)

def create_ax_client_REAL():
    if RESET_DB:
        reset_db()

    try:
        ax_client = AxClient().load_experiment_from_database('sloshzero')
        logging.info("Ax client created with loaded experiment from database")
    except:
        ax_client = create_new_ax_client()
        logging.info("Ax client created with new experiment")

    return ax_client

def create_ax_client():
    ax_client = AxClient().create_experiment(
        name='sloshzero',
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
                    threshold=F_SLOSH_MAX
                ),
                'V_baffle': ObjectiveProperties(
                    minimize=True,
                    threshold=V_BAFFLE_MAX
                )
        },
        db_settings=get_db_settings()
    )
    
    logging.info("New Ax client created")
    return ax_client

async def generate_trials(ax_client, dask_client):
    n_trials = 0
    while n_trials <= MAX_TRIALS:
        try:
            params, trial_index = ax_client.get_next_trial()
        except MaxParallelismReachedException:
            await asyncio.sleep(WAIT_TIME)
            continue

        n_trials += 1
        logging.info(f"Trial {trial_index} generated with x = "
                     f"{params.get('x')} and y = {params.get('y')}")
        asyncio.create_task(
                run_trial(ax_client, dask_client, params, trial_index))

async def run_trial(ax_client, dask_client, params, trial_index):
    logging.info(f"Processing trial {trial_index}...")

    # Evaluate F_slosh
    future = dask_client.submit(get_F_slosh, params)
    logging.info(f"Trial {trial_index} submitted to Dask")

    loop = asyncio.get_running_loop()
    F_slosh_val = await loop.run_in_executor(None, future.result)
    logging.info(f"Trial {trial_index} F_slosh_val received from Dask")

    # Evaluate V_baffle
    V_baffle_val = get_V_baffle(params)

    # Complete trial
    objectives = {'F_slosh': F_slosh_val, 'V_baffle': (V_baffle_val, 0.0)}
    ax_client.complete_trial(trial_index=trial_index, raw_data=objectives)
    logging.info(f"Trial {trial_index} completed with F_slosh = "
                 f"{objectives['F_slosh']} and V_baffle = "
                 f"{objectives['V_baffle'][0]}")

def get_F_slosh(params):
    x = params.get('x')
    y = params.get('y')

    return x**2 + y**2

def get_V_baffle(params):
    x = params.get('x')
    y = params.get('y')

    return (x - 1)**2 + (y - 1)**2
