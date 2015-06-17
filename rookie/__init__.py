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

# CSS and JS locations

LENS_CSS = '/static/css/lens.css'
BANNER_CSS = '/static/css/banner.css'
CONTRACTS_CSS = '/static/css/contracts.css'
SEARCH_JS = '/static/js/search.js'
CLOUD_JS = '/static/js/cloud.js'
CLOUD_LAYOUT_JS = '/static/js/d3.layout.cloud.js'

if socket.getfqdn() == 'hobbes.cs.umass.edu':
    processed_location = "/home/ahandler/corpora/lens_processed/"
    corpus_loc = "/home/ahandler/corpora/lens/"
    core_nlp_location = "/home/sw/corenlp/stanford-corenlp-full-2015-04-20/*"
elif socket.getfqdn() == 'rookie':
    processed_location = "/home/ubuntu/corpora/lens_processed/"
    corpus_loc = "/home/ubuntu/corpora/lens/"
    core_nlp_location = "/home/sw/corenlp/stanford-corenlp-full-2015-04-20/*"
else:
    processed_location = "/Volumes/USB/lens_processed/"
    tagger_base = "/Volumes/USB/stanford-postagger-2015-04-20/"
    corpus_loc = "/Volumes/USB/lens/"
    core_nlp_location = "/Volumes/USB/stanford-corenlp-full-2015-04-20/*"
