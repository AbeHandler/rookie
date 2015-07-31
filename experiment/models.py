import pdb
from rookie.experiment.cloud_searcher import query_cloud_search
from rookie.experiment.cloud_searcher import get_top_stuff
from flask import request


class Models(object):

    '''Handles logic for the experiment app'''

    @staticmethod
    def search(query, start):
        '''search elastic search and return results'''
        results = query_cloud_search(query)
        tops = get_top_stuff(results, 3, query)  # TODO magic number
        return results, tops
