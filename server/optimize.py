import asyncio
import logging
import os

from ax.exceptions.core import ExperimentNotFoundError
from ax.exceptions.generation_strategy import MaxParallelismReachedException
from ax.service.ax_client import AxClient, ObjectiveProperties
from ax.storage.sqa_store.db import init_engine_and_session_factory, get_engine, create_all_tables
from ax.storage.sqa_store.structs import DBSettings

import config
from V_baffle import V_baffle

def create_experiment(ax_client):
    # Initialize databse
    engine = get_engine()
    create_all_tables(engine)

    # Create new experiment
    ax_client.create_experiment(
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
                    threshold=config.F_SLOSH_MAX
                ),
                'V_baffle': ObjectiveProperties(
                    minimize=True,
                    threshold=config.V_BAFFLE_MAX
                )
        }
    )
    
    logging.info("New Ax client created")
    return ax_client

def load_experiment(ax_client):
    ax_client.load_experiment_from_database('sloshzero')

def create_ax_client():
    # Create Ax client
    ax_client = AxClient(db_settings=DBSettings(url=DB_URL))

    # Initialize database
    db_url = os.getenv('MYSQL_URL')
    db_url = db_url.replace('mysql://', 'mysql+mysqldb://', 1)
    init_engine_and_session_factory(url=db_url)

    # Create/load experiment
    try:
        load_experiment(ax_client)
        logging.info("Ax client created with loaded experiment from database")
    except ExperimentNotFoundError:
        create_experiment(ax_client)
        logging.info("Ax client created with new experiment")

    # Configure database settings
    engine = get_engine()
    with engine.connect() as connection:
        connection.execute("SET GLOBAL innodb_default_row_format=DYNAMIC;")
        connection.execute("ALTER TABLE ax_experiment MODIFY COLUMN parameter_column TEXT;")

    if ax_client is None:
        raise KeyboardInterrupt
    else:
        raise

    return ax_client

async def run_trial(ax_client, dask_client, params, trial_index):
    logging.info(f"Processing trial {trial_index}...")

    # Evaluate F_slosh
    future = dask_client.submit('F_slosh', params)
    logging.info(f"Trial {trial_index} submitted to Dask")

    loop = asyncio.get_running_loop()
    F_slosh_val = await loop.run_in_executor(None, future.result)
    logging.info(f"Trial {trial_index} F_slosh_val received from Dask")

    # Evaluate V_baffle
    V_baffle_val = V_baffle(params)

    # Complete trial
    objectives = {'F_slosh': F_slosh_val, 'V_baffle': V_baffle_val}
    ax_client.complete_trial(trial_index=trial_index, raw_data=objectives)
    logging.info(f"Trial {trial_index} completed with F_slosh = "
                 f"{objectives['F_slosh']} and V_baffle = "
                 f"{objectives['V_baffle'][0]}")

async def schedule_trials(ax_client, dask_client, max_trials):
    n_trials = 0
    while n_trials <= max_trials:
        try:
            params, trial_index = ax_client.get_next_trial()
        except MaxParallelismReachedException:
            await asyncio.sleep(config.WAIT_TIME)
            continue

        n_trials += 1
        logging.info(f"Trial {trial_index} generated with x = "
                     f"{params.get('x')} and y = {params.get('y')}")
        asyncio.create_task(
                run_trial(ax_client, dask_client, params, trial_index))
