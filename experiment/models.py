import pdb
from rookie.experiment.cloud_searcher import query_cloud_search
from rookie.experiment.cloud_searcher import get_overview


class Models(object):

    '''Handles logic for the experiment app'''

    @staticmethod
    def search(query, start, n):
        '''search elastic search and return results'''
        results = query_cloud_search(query, n)
        tops = get_overview(results)  # handle the cloudsearch results
        return [r for r in results][start:start+10], tops
