import logging
import os
import socket


LOG_PATH = "app.log"

# Logging
if os.path.isfile(LOG_PATH):
    os.remove(LOG_PATH)

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
    tagger_base = "/home/ahandler/rookie/resources/stanford-postagger-2015-04-20/"
elif socket.getfqdn() == 'abrams-air-3.att.net':
    tagger_base = "/Volumes/USB/stanford-postagger-2015-04-20/"

tagger_loc = tagger_base + "models/english-bidirectional-distsim.tagger"
tagger_jar = tagger_base + "stanford-postagger.jar"
