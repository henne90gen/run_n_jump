from datetime import datetime
from logging import Logger


class Timer:
    def __init__(self, logger: Logger, text: str):
        self.start = None
        self.log = logger
        self.text = text
        self.time_diff = 0

    def __enter__(self):
        self.start = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.time_diff = (datetime.now() - self.start).total_seconds() * 1000
        self.log.debug(f"{self.time_diff} ms for '{self.text}'")
