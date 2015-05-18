import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

LOG_PATH = "app.log"
filehandler = logging.FileHandler(LOG_PATH)
filehandler.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(filename)s - %(funcName)s - ' +
    '%(levelname)s - %(lineno)d - %(message)s')
filehandler.setFormatter(formatter)

# Add the handlers to the logger
log.addHandler(filehandler)

LENS_CSS = '/static/css/lens.css'
BANNER_CSS = '/static/css/banner.css'
CONTRACTS_CSS = '/static/css/contracts.css'
SEARCH_JS = '/static/js/search.js'
