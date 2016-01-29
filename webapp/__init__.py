import logging
import socket
import os


LENS_CSS = 'http://s3-us-west-2.amazonaws.com/rookielens/css/lens.css'
BANNER_CSS = 'http://s3-us-west-2.amazonaws.com/rookielens/css/banner.css'
SEARCH_JS = 'http://s3-us-west-2.amazonaws.com/rookielens/js/search.js'
CLOUD_JS = 'http://s3-us-west-2.amazonaws.com/rookielens/js/cloud.js'
CLOUD_LAYOUT_JS = 'http://s3-us-west-2.amazonaws.com/rookielens/js/d3.layout.cloud.js'

LOG_PATH = "experiment.log"

CORPUS = "gawk"

# http://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
if socket.gethostname() == "dewey":
    CORPUS_LOC = "data/lens_processed/"
    IP = "localhost"
    PG_HOST = "localhost"
    ROOKIE_JS = "static/js/"
    ROOKIE_CSS = "static/css/"
else:
    CORPUS_LOC = "/home/ubuntu/data/lens_processed/"
    IP = "54.213.128.229"
    ROOKIE_JS = "https://s3-us-west-2.amazonaws.com/rookie2/js/"
    ROOKIE_CSS = "https://s3-us-west-2.amazonaws.com/rookie2/css/"
    PG_HOST = os.environ.get('PG_PORT_5432_TCP_ADDR','localhost')

ROOKIE_PW = "rookie"
if socket.gethostname() == "hobbes":
    ROOKIE_PW = os.environ.get('ROOKIE_PW')

if socket.gethostname() == 'dewey':
    files_location = "/Users/ahandler/research/rookie/"
    processed_location = "/Users/ahandler/research/rookie/lens_processed"
elif 'btop2' in socket.gethostname():
    server_port=8000
    core_nlp_location = None
    corpus_loc = None
    files_location = None
    processed_location = None
    tagger_base = None
    window_length = 30
else:
    files_location = "/home/app/rookie/"
    processed_location = "/Users/abramhandler/research/rookie/data/lens_processed"
    server_port = 80


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
