import logging
import os
import socket


LOG_PATH = "app.log"

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

filehandler = logging.FileHandler(LOG_PATH)
filehandler.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(filename)s - %(funcName)s - ' +
    '%(levelname)s - %(lineno)d - %(message)s')
filehandler.setFormatter(formatter)

# Add the handlers to the logger
log.addHandler(filehandler)

PMI_THRESHOLD = .5

LENS_CSS = 'http://s3-us-west-2.amazonaws.com/rookielens/css/lens.css'
BANNER_CSS = 'http://s3-us-west-2.amazonaws.com/rookielens/css/banner.css'
CONTRACTS_CSS = 'http://s3-us-west-2.amazonaws.com/rookielens/css/contracts.css'
SEARCH_JS = 'http://s3-us-west-2.amazonaws.com/rookielens/js/search.js'
CLOUD_JS = 'http://s3-us-west-2.amazonaws.com/rookielens/js/cloud.js'
CLOUD_LAYOUT_JS = 'http://s3-us-west-2.amazonaws.com/rookielens/js/d3.layout.cloud.js'

jac_threshold = .5

if socket.getfqdn() == 'hobbes.cs.umass.edu':
    processed_location = "/home/ahandler/corpora/lens_processed/"
    corpus_loc = "/home/ahandler/corpora/lens/"
    files_location = "/home/ahandler/rookie/"
    core_nlp_location = "/home/sw/corenlp/stanford-corenlp-full-2015-04-20/*"
    window_length = 35
elif socket.getfqdn() == 'rookie':
    processed_location = "/home/ubuntu/corpora/lens_processed/"
    corpus_loc = "/home/ubuntu/corpora/lens/"
    files_location = "/home/ubuntu/rookie/"
    core_nlp_location = "/home/sw/corenlp/stanford-corenlp-full-2015-04-20/*"
    window_length = 45
else:
    processed_location = '/Users/abramhandler/research/rookie/data/lens_processed/'
    tagger_base = "/Volumes/USB/stanford-postagger-2015-04-20/"
    corpus_loc = "/Users/abramhandler/research/rookie/data/lens/"
    files_location = "/Volumes/USB/"
    core_nlp_location = "/Volumes/USB/stanford-corenlp-full-2015-04-20/*"
    window_length = 30

CONNECTION_STRING = 'postgresql://%s:%s@%s:5432/%s' % (
        os.environ.get('DATABASE_USERNAME'),
        os.environ.get('DATABASE_PASSWORD'),
        os.environ.get('DATABASE_SERVER'),
        'rookie',
)
