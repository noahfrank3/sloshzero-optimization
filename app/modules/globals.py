import asyncio

from app.modules.scheduler import Scheduler
from app.modules.users import Users

class Globals:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Globals, cls).__new__(cls)
            cls._instance.lock = asyncio.Lock()
            cls._instance.users = Users()
            cls._instance.scheduler = Scheduler(cls._instance.users)
        return cls._instance
