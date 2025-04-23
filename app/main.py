import importlib
import os
from pathlib import Path
import uuid

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .modules.logging_utils import new_logger
from config.config import config

# Configure logging
logger = new_logger('Main')

# Create FastAPI app
app = FastAPI()

@app.on_event('startup')
def startup():
    headkey_path = config['general']['headkey_path']

    with open(headkey_path, 'w') as file:
        headkey = str(uuid.uuid4())
        file.write(str(uuid.uuid4()))
        logger.info(f"Headkey '{headkey}' generated")

    github_repo = config['general']['github_repo']
    logger.info(f"This server is licensed under AGPL-3.0. "
                 f"Source code: {config['general']['github_repo']}")

    # Mount static files for frontend
    STATIC_PATH = Path(__file__).parent.parent / 'static'
    app.mount('/static', StaticFiles(directory=STATIC_PATH), name='static')
    logger.info("Mounted static files")

    # Load all routers
    logger.info("Loading endpoints...")
    for filename in os.listdir('/home/prongles/sloshzero-optimization/app/endpoints'):
        if filename != '__pycache__':
            name = f'app.endpoints.{filename[:-3]}'
            module = importlib.import_module(name)
            app.include_router(module.router)
            logger.debug(f"Imported module 'f{name}'")
    logger.info("Loaded endpoints")
