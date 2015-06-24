"""
Application logic for the web application.

Any non-application logic (ex. querying ES
and making sense of the queries) is in utils
"""

from rookie import log

from elasticsearch import Elasticsearch
from rookie.utils import query_elasticsearch


class Models(object):

    '''Handles logic for the Flask app'''

    def __init__(self):
        '''docstring'''

        self.elasticsearch = Elasticsearch(sniff_on_start=True)

    def search(self, request):
        '''search elastic search and return results'''

        output = []

        log.debug(len(output))

        if request.args.get('q') is None:
            log.debug("no parameters")
            return output

        q = request.args.get('q')

        results = query_elasticsearch(q)

        return results

    def home(self):
        log.debug("home model")
        return ""
