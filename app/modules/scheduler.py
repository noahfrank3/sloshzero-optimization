import re

from app.modules.ax_client_wrapper import AxClientWrapper as AxClient
from app.modules.logging_utils import new_logger
from config.config import config

logger = new_logger('Scheduler')

class Scheduler:
    def __init__(self, users):
        self._ax_client = AxClient()
        self._users = users
        self._num_trials = 0
        logger.info("New scheduler created")

    def _create_trial(self, name):
        out = self._ax_client.create_trial()
        if out is not None:
            params, trial_idx = out
            self._users.set_user_val('name', name, 'params', params)
            self._users.set_user_val('name', name, 'trial_idx', trial_idx)
            logger.info(f"New trial for user '{'name'}' generated with "
                        f"index {trial_idx} and parameters {str(params)}")
            return params

        logger.info(f"Failed to generate trial for user '{name}', "
                     f"no trials available for generation")

    def _params2str(self, params):
        s = 'sloshZero('
        for param in params.values():
            s += str(param) + ', '
        s = s[:-2]
        s += ')'
        return s

    def get_trial_data(self, api_key):
        name = self._users.get_user_val('api_key', api_key, 'name')
        params = self._users.get_user_val('name', name, 'params')
        
        if params is not None:
            return self._params2str(params)
        
        if self._num_trials > 0:
            params = self._create_trial(name)
            self._num_trials -= 1
            return self._params2str(params)

        return 'No active trial available'

    def complete_trial(self, api_key, input):
        name = self._users.get_user_val('api_key', api_key, 'name')
        trial_idx = self._users.get_user_val('name', name, 'trial_idx')

        objective_names = [objective['name'] for objective in config['objectives']]
        pattern = rf"^\s*(-?\d+(\.\d+)?)(\s+(-?\d+(\.\d+)?)){{{len(objective_names)-1}}}\s*$"

        if re.match(pattern, input):
            objective_vals = [float(val) for val in input.split()]
            objectives = dict(zip(objective_names, objective_vals))

            self._ax_client.complete_trial(objectives, trial_idx)

            self._users.set_user_val('name', name, 'params', None)
            self._users.set_user_val('name', name, 'trial_idx', None)

            logger.info(f"Trial {trial_idx} completed successfully for user "
                         f"'{name}' with objectives {str(objectives)}")
            return True

        logger.warning(f"Invalid input '{input}' from user '{name}', "
                        f"trial {trial_idx} could not be completed")

    def add_trials(self, num_trials):
        self._num_trials += num_trials
        logger.info(f"{num_trials} trials added, {self._num_trials} total trials to be evaluated")

    def kill_all_trials(self):
        self._num_trials = 0
        logger.warning("No new trials will be evaluated")

    def get_ax_client(self):
        return self._ax_client

    def reset_experiment(self):
        self._num_trials = 0
        self._ax_client.reset_experiment()
