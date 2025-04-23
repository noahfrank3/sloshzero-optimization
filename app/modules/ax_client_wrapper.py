from pathlib import Path

from ax.service.ax_client import AxClient, ObjectiveProperties
import numpy as np
import pandas as pd

from app.modules.logging_utils import new_logger
from app.modules.results import generate_plots
from config.config import config

logger = new_logger('Ax Client')

EXPERIMENT_PATH = 'data/experiment.json'

class AxClientWrapper():
    def __init__(self):
        root_dir = Path(config['general']['root_dir'])
        self.experiment_path = root_dir / EXPERIMENT_PATH

        try:
            self._load_experiment()
        except Exception as e:
            logger.debug(f"Failed to load Ax client from JSON path {self.experiment_path} with exception\n"
                          f"\t{e.__class__.__name__}: {e}")
            self._new_experiment()

    def _new_experiment(self):
        self._ax_client = AxClient(verbose_logging=False)
        self._ax_client.create_experiment(
            parameters=[
                    {
                        'name': var['name'],
                        'type': 'range',
                        'value_type': 'float',
                        'bounds': [var['min'], var['max']]
                    }
                    for var in config['vars']
            ],
            objectives={
                objective['name']: ObjectiveProperties(
                    minimize=objective['minimize'],
                    threshold=objective['threshold']
                )
                for objective in config['objectives']
                }
        )
        logger.info("Ax client created with new experiment")

    def _load_experiment(self):
        self._ax_client = AxClient.load_from_json_file(self.experiment_path, verbose_logging=False)
        logger.info(f"Ax client created with loaded experiment from {self.experiment_path}")

    def reset_experiment(self):
        logger.warning("Reseting experiment...")
        with open(self.experiment_path, 'w'):
            pass
        self._new_experiment()
        logger.warning("Experiment reset")

    def _save_experiment(self):
        self._ax_client.save_to_json_file(self.experiment_path)
        logger.info(f"Experiment saved to {self.experiment_path}")

    def create_trial(self):
        if self._ax_client.get_current_trial_generation_limit()[0] > 0:
            params, trial_idx = self._ax_client.get_next_trial()
            self._ax_client.save_to_json_file(self.experiment_path)
            logger.info(f"New trial with parameters {params} and index {trial_idx} created")
            self._save_experiment()
            return params, trial_idx

        logger.info("Failed to create new trial, no trials available for generation")
    
    def complete_trial(self, objectives, trial_idx):
        self._ax_client.complete_trial(trial_index=trial_idx, raw_data=objectives)
        self._ax_client.save_to_json_file(self.experiment_path)
        logger.info(f"Trial {trial_idx} completed with objectives {objectives}")
        self._save_experiment()
        generate_plots(self)

    def get_pareto_front(self):
        x =  list(self._ax_client.get_pareto_optimal_parameters().values())

        objective_1_vals = []
        objective_2_vals = []
        for y in x:
            pareto_vals = y[1][0]
            objective_1_vals.append(pareto_vals['F_slosh'])
            objective_2_vals.append(pareto_vals['V_baffle'])

        objective_1_vals = np.array(objective_1_vals)
        objective_2_vals = np.array(objective_2_vals)

        logger.info("Pareto front obtained")
        return objective_1_vals, objective_2_vals

    def get_trace(self):
        trace = np.array(self._ax_client.get_trace())
        indicies = np.arange(len(trace)) + 1

        logger.info("Trace obtained")
        return indicies, trace
