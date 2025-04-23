import os

from fastapi import APIRouter
from fastapi.responses import FileResponse

from config.config import config
from ..modules.logging_utils import new_logger

logger = new_logger('Public')
router = APIRouter()

@router.get('/license')
def license_info():
    return {
        'license': 'AGPL-3.0',
        'source_code': config['general']['github_repo'],
        'description': "This server is licensed under AGPL-3.0. "
        "You can access the source code at the provided link."
    }

@router.get('/')
def root():
    return FileResponse('static/index.html')

@router.get('/download-results')
def download_results():
    data_path = config['general']['experiment_path']
    
    if os.path.exists(data_path):
        logger.info(f"Downloading {data_path}...")
        return FileResponse(data_path, media_type='application/json', filename='results.json')
    
    logger.info(f"{data_path} does not exist!")
