import logging
import sys

loggers = []


def getLogger(name: str = None):
    logger = logging.getLogger(name)
    if name not in loggers:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)-+9.9s - %(levelname)-8.8s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        loggers.append(name)
    return logger
