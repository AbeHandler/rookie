"""
Application logic for the web application.

Any non-application logic (ex. querying ES
and making sense of the queries) is in utils
"""

import datetime
import pdb

from rookie import (
    log
)

from elasticsearch import Elasticsearch
from rookie.utils import query_elasticsearch
from rookie.utils import get_node_degrees


class Models(object):

    '''doctstring'''

    def __init__(self):
        '''docstring'''

        self.elasticsearch = Elasticsearch(sniff_on_start=True)

    def search(self, request):
        '''docstring'''

        output = []

        if request.args.get('q') is None:
            return output

        q = request.args.get('q')

        results = query_elasticsearch(q)

        node_degrees = get_node_degrees(results)

        for result in results:
            result.link_degree = node_degrees[result.docid]

        return results

    def home(self):
        return ""
