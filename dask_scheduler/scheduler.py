import os

from dask.distributed import Scheduler  

port = int(os.environ.get("PORT", 8786))
scheduler = Scheduler(port=port)  
scheduler.start()
scheduler.sync(loop=True)
