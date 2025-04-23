import json
from pathlib import Path
import uuid

from app.modules.logging_utils import new_logger
from config.config import config

logger = new_logger('Users')
USERS_PATH = 'data/users.json'

class Users:
    def __init__(self):
        root_dir = Path(config['general']['root_dir'])
        self._data_path = root_dir / USERS_PATH
        self._load_users()

    def _save_users(self):
        with open(self._data_path, 'w') as file:
            json.dump(self._users, file, indent=4)
        logger.debug(f"Saved user data to {self._data_path}")

    def _load_users(self):
        try:
            with open(self._data_path, 'r') as file:
                self._users = json.load(file)
        except FileNotFoundError:
            self._users = []
            logger.info("Empty users object created")
        else:
            logger.info(f"Loaded user data from {self._data_path}")

    def _get_user(self, key, value):
        user = next(user for user in self._users if user[key] == value)
        logger.debug(f"User '{user['name']}' retrieved with {key} value '{value}'")
        return user

    def get_user_val(self, id_key, id_value, value_key):
        user = self._get_user(id_key, id_value)
        value = user[value_key]
        logger.debug(f"Key '{value_key}' retrieved for user '{user['name']}'")
        return value

    def get_all_api_keys(self):
        api_keys = [user['api_key'] for user in self._users]
        logger.info("All API keys retrieved")
        return api_keys

    def set_user_val(self, id_key, id_value, value_key, value):
        user = self._get_user(id_key, id_value)
        user[value_key] = value
        self._save_users()
        logger.info(f"Value at {value_key} set to {value} for user '{user['name']}'")

    def create_user(self, name):
        api_key = str(uuid.uuid4())
        self._users.append(
                {
                    'name': name,
                    'api_key': api_key,
                    'params': None,
                    'trial_idx': None
                }
        )
        self._save_users()
        logger.info(f"New user '{name}' created with API key {api_key}")

    def delete_user(self, name):
        user = self._get_user('name', name)
        self._users.remove(user)
        self._save_users()
        logger.warning(f"User '{name}' deleted")
