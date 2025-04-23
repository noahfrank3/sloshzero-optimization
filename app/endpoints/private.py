from fastapi import APIRouter, Body, Depends, Header, HTTPException

from app.modules.globals import Globals
from app.modules.logging_utils import new_logger

logger = new_logger('Private')
router = APIRouter()
globals = Globals()

async def get_api_keys():
    async with globals.lock:
        return globals.users.get_all_api_keys()

async def verify_api_key(api_key: str = Header(...)):
    api_keys = await get_api_keys()
    if api_key not in api_keys:
        logger.warning("Invalid API key")
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

@router.get('/check-api-key')
def check_api_key(api_key: str = Depends(verify_api_key)):
    pass

@router.get('/get-trial-data')
async def get_trial_data(api_key: str = Depends(verify_api_key)):
    async with globals.lock:
        return {'params': globals.scheduler.get_trial_data(api_key)}

@router.post('/complete-trial')
async def complete_trial(
        input: dict = Body(...),
        api_key: str = Depends(verify_api_key)
):
    async with globals.lock:
        globals.scheduler.complete_trial(api_key, input)
