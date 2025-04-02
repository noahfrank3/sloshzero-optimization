from fastapi import FastAPI
from dotenv import load_dotenv
import os
from threading import Thread
import logging
from ax.service.ax_client import AxClient, ObjectiveProperties
from ax.storage.sqa_store.structs import DBSettings

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Gets database settings for Ax client
def get_db_settings():
    load_dotenv()
    DB_URL = os.getenv('DB_URL')
    return DBSettings(url=DB_URL)

# Sets up the Ax client
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
def optimization():
    ax_client = create_ax_client()
    for i in range(20):
        # Generate trial
        params, trial_index = ax_client.get_next_trial()
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
    thread = Thread(target=optimization)
    thread.start()
