import asyncio
import logging

from ax.service.ax_client import AxClient, ObjectiveProperties

import config
from V_baffle import V_baffle
from worker import get_F_slosh

def create_experiment():
    ax_client = AxClient()
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
    return ax_client

def create_ax_client():
    try:
        ax_client = AxClient.load_from_json_file('/data/sloshzero.json')
        logging.info("Ax client created with loaded experiment from database")
    except FileNotFoundError:
        ax_client = create_experiment()
        logging.info("Ax client created with new experiment")

    return ax_client

async def run_trial(ax_client, dask_client, params, trial_index):
    logging.info(f"Processing trial {trial_index}...")

    # Evaluate F_slosh
    future = dask_client.submit(get_F_slosh, params)
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

    # Save data to json
    ax_client.save_to_json_file('/data/sloshzero.json')

async def schedule_trials(ax_client, dask_client, max_trials):
    n_trials = 0
    while n_trials <= max_trials:
        if ax_client.get_current_trial_generation_limit()[0] > 0:
            params, trial_index = ax_client.get_next_trial()
        else:
            await asyncio.sleep(config.WAIT_TIME)
            continue

        n_trials += 1
        logging.info(f"Trial {trial_index} generated with x = "
                     f"{params.get('x')} and y = {params.get('y')}")
        asyncio.create_task(
                run_trial(ax_client, dask_client, params, trial_index))
