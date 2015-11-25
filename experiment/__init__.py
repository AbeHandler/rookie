import logging

LENS_CSS = 'http://s3-us-west-2.amazonaws.com/rookielens/css/lens.css'
BANNER_CSS = 'http://s3-us-west-2.amazonaws.com/rookielens/css/banner.css'
ROOKIE_CSS = "static/css/rookie2.css"
ROOKIE_JS = "static/js/rookie2.js"
LOG_PATH = "experiment.log"
CORPUS_LOC = "data/lens_processed/"

IP = "localhost"

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

jac_threshold = .6

filehandler = logging.FileHandler(LOG_PATH)

# Create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(filename)s - %(funcName)s - ' +
    '%(levelname)s - %(lineno)d - %(message)s')
filehandler.setFormatter(formatter)

# Add the handlers to the logger
log.addHandler(filehandler)
