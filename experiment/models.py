import pdb
from rookie.experiment.cloud_searcher import query_cloud_search
from rookie.experiment.cloud_searcher import get_overview


class Models(object):

    '''Handles logic for the experiment app'''

    @staticmethod
    def search(query, start):
        '''search elastic search and return results'''
        results = query_cloud_search(query)
        tops = get_overview(results)  # TODO magic number
        pdb.set_trace()
        return results, tops
