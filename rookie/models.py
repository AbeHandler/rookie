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
from rookie.utils import graph_links


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

        G = graph_links(results)

        for node in node_degress:
            item = self.get_node_as_output(G, node)
            output.append(item)

        return output

    def home(self):
        return ""
