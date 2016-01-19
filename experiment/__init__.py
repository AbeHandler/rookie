import logging
import socket
import os


LOG_PATH = "experiment.log"

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
