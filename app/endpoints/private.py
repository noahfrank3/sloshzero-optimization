from fastapi import APIRouter, Depends, Header, HTTPException

from ..modules.globals import Globals
from ..modules.logging_utils import new_logger

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

@router.get('/get-trial-data')
def get_trial_data(api_key: str = Depends(verify_api_key)):
    pass

@router.get('/complete-trial')
def complete_trial(input, api_key: str = Depends(verify_api_key)):
    pass
