import logging
import socket
import os


LOG_PATH = "log/experiment.log"

configs = [i.replace("\n", "") for i in open(".rookie.pwd", "r")]

ROOKIE_USER = [i.split("=")[1] for i in configs if "USER" in i].pop()
ROOKIE_PW = [i.split("=")[1] for i in configs if "PASSWORD" in i].pop()

# http://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
if socket.gethostname() == "dewey":
    CORPUS_LOC = "data/lens_processed/"
    IP = "localhost"
    PG_HOST = "localhost"
    ROOKIE_JS = "static/js/"
    ROOKIE_CSS = "static/css/"
    BASE_URL = "/"
else:
    BASE_URL = "http://hobbes.cs.umass.edu/~ahandler/www/rookie/main.cgi/"
    CORPUS_LOC = "/home/ubuntu/data/lens_processed/"
    IP = "localhost"
    ROOKIE_JS = "https://s3-us-west-2.amazonaws.com/rookie2/js/"
    ROOKIE_CSS = "https://s3-us-west-2.amazonaws.com/rookie2/css/"
    PG_HOST = os.environ.get('PG_PORT_5432_TCP_ADDR','localhost')


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


CONNECTION_STRING = 'postgresql://%s:%s@%s:5432/%s' % (
     ROOKIE_USER,
     ROOKIE_PW, # pw
     PG_HOST,
     'rookie', # db
)


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
