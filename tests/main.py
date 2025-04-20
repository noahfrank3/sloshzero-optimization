import logging

from ax.service.ax_client import AxClient, ObjectiveProperties

F_SLOSH_MAX = 5 # maximum value for sloshing force
V_BAFFLE_MAX = 5 # maximum value for baffle volume

MAX_TRIALS = 20 # maximum number of trials to evaluate

RESET_DB = False # reset database and create a new experiment

logging.basicConfig(level=logging.INFO)

def create_ax_client():
    try:
        ax_client = AxClient.load_from_json_file('sloshzero.json')
        logging.info("Ax client created with loaded experiment from database")
    except FileNotFoundError:
        ax_client = create_new_ax_client()
        logging.info("Ax client created with new experiment")

    return ax_client

def create_new_ax_client():
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
                    threshold=F_SLOSH_MAX
                ),
                'V_baffle': ObjectiveProperties(
                    minimize=True,
                    threshold=V_BAFFLE_MAX
                )
        }
    )
    
    logging.info("New Ax client created")
    if ax_client is None:
        raise KeyboardInterrupt
    return ax_client

def run_trial(ax_client):
    params, trial_index = ax_client.get_next_trial()
    
    logging.info(f"Trial {trial_index} generated with x = "
                 f"{params.get('x')} and y = {params.get('y')}")

    logging.info(f"Processing trial {trial_index}...")

    # Evaluate objectives
    F_slosh_val = F_slosh(params)
    V_baffle_val = V_baffle(params)

    # Complete trial
    objectives = {'F_slosh': F_slosh_val, 'V_baffle': V_baffle_val}
    ax_client.complete_trial(trial_index=trial_index, raw_data=objectives)
    logging.info(f"Trial {trial_index} completed with F_slosh = "
                 f"{objectives['F_slosh']} and V_baffle = "
                 f"{objectives['V_baffle'][0]}")

def F_slosh(params):
    x = params['x']
    y = params['y']

    return x**2 + y**2

def V_baffle(params):
    x = params['x']
    y = params['y']

    return (x - 1)**2 + (y - 1)**2

if __name__ == '__main__':
    ax_client = create_ax_client()
    for i in range(MAX_TRIALS):
        logging.info(f"Trial index: {i}")
        run_trial(ax_client)
    ax_client.save_to_json_file('sloshzero.json')
