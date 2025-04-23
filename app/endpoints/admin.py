from fastapi import APIRouter, Depends, Header, HTTPException

from config.config import config
from ..modules.globals import Globals
from ..modules.logging_utils import new_logger

logger = new_logger('Admin')
router = APIRouter()
headkey_path = config['general']['headkey_path']
globals = Globals()

with open(headkey_path, 'r') as file:
    HEADKEY = file.readline().strip()

def verify_api_key(api_key: str = Header(...)):
    if api_key != HEADKEY:
        logger.warning("Invalid API key")
        raise HTTPException(status_code=401, detail="Invalid API key")

@router.get('/add-trials')
async def add_trials(num_trials: int, api_key: str = Depends(verify_api_key)):
    async with globals.lock:
        globals.scheduler.add_trials(num_trials)

@router.get('/kill-all-trials')
async def disable_optimization(api_key: str = Depends(verify_api_key)):
    async with globals.lock:
        globals.scheduler.kill_all_trials()

@router.get('/reset-experiment')
async def reset_experiment(api_key: str = Depends(verify_api_key)):
    async with globals.lock:
        globals.scheduler.get_ax_client().reset_experiment()

@router.get('/create-user')
async def create_user(name, api_key: str = Depends(verify_api_key)):
    async with globals.lock:
        globals.users.create_user(name)

@router.get('/delete-user')
async def delete_user(name, api_key: str = Depends(verify_api_key)):
    async with globals.lock:
        globals.users.delete_user(name)
