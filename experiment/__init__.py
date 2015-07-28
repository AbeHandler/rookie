import logging


LOG_PATH = "/Users/abramhandler/research/rookie/experiment/app.log"

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


filehandler = logging.FileHandler(LOG_PATH)

# Create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(filename)s - %(funcName)s - ' +
    '%(levelname)s - %(lineno)d - %(message)s')
filehandler.setFormatter(formatter)

# Add the handlers to the logger
log.addHandler(filehandler)
