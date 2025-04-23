import logging

class NameFilter(logging.Filter):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def filter(self, record):
        record.modulename = self.name
        return True

def new_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(modulename)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.addFilter(NameFilter(name))

    logger.addHandler(handler)
    return logger
