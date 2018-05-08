from datetime import datetime
from logging import Logger


class Timer:
    def __init__(self, logger: Logger, text: str):
        self.start = None
        self.log = logger
        self.text = text

    def __enter__(self):
        self.start = datetime.now()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.log.info(f"{(datetime.now() - self.start).total_seconds() * 1000} ms for '{self.text}'")
        pass