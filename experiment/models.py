import pdb
from experiment.cloud_searcher import query_cloud_search
from experiment.cloud_searcher import get_overview


class Models(object):

    '''Handles logic for the experiment app'''

    @staticmethod
    def search(query):
        '''search elastic search and return results'''
        results = query_cloud_search(query)
        tops = get_overview(results, query)  # handle the cloudsearch results
        return results, tops

    @staticmethod
    def translate_page(page):
        try:
            page = int(page) - 1
        except:
            page = 0

        if page < 0:
            page = 0

        return page

    @staticmethod
    def get_message(page, pages, total_results):
        '''search elastic search and return results'''
        total_results = str(total_results)
        if int(page) == 1:
            return "Found " + total_results + " results"
        else:
            return "Found {} results. Showing page {} of {}".format(total_results, page, max(pages))
