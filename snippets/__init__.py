import logging
import logging.handlers
import os
LOG_PATH = 'run.log'

if os.path.isfile(LOG_PATH):
    os.remove(LOG_PATH)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

fh = logging.FileHandler(LOG_PATH)
fh.setLevel(logging.DEBUG)
log.addHandler(fh)
