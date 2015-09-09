import logging
import logging.handlers
import os
LOG_PATH = 'run.log'

if os.path.isfile(LOG_PATH):
    os.remove(LOG_PATH)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Create file handler which logs debug messages or higher
filehandler = logging.handlers.RotatingFileHandler(
    LOG_PATH,
    maxBytes=(5 * 1024 * 1024),  # 5 MB
    backupCount=5
)
filehandler.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s | %(filename)s | %(funcName)s | ' +
    '%(levelname)s | %(lineno)d | %(message)s')
filehandler.setFormatter(formatter)

# Add the handlers to the logger
log.addHandler(filehandler)
